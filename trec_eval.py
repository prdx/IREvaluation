import argparse
import math
import texttable as tt

# Initialize some arrays.
recalls = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
cutoffs = (5, 10, 15, 20, 30, 100, 200, 500, 1000)

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            data = f.read()
            data = data.split("\n")
            data.pop()
            return data
    except Exception as e:
        print(e)
        raise IOError

def build_qrel(qrel_data):
    """ %qrel is a hash whose keys are topic IDs and whose values are
    references to hashes.  Each referenced hash has keys which are
    doc IDs and values which are relevance values.  In other words...

    %qrel				The qrel hash.
    $qrel{$topic}			Reference to a hash for $topic.
    $qrel{$topic}->{$doc_id}	The relevance of $doc_id in $topic.
    """
    qrel = {}
    for line in qrel_data:
        q_id, author, doc_id, relevance = line.split()
        try:
            qrel[q_id][doc_id] = int(relevance)
        except KeyError:
            qrel[q_id] = {}
            qrel[q_id][doc_id] = int(relevance) 
    return qrel

def build_num_rel(qrel):
    """ %num_rel    Hash whose values are (expected) number
                    of docs relevant for each topic.
    """
    num_rel = {}
    for topic in qrel:
        for doc in qrel[topic]:
            if topic in num_rel:
                if qrel[topic][doc] > 0:
                    num_rel[topic] += 1
            else:
                if qrel[topic][doc] > 0:
                    num_rel[topic] = 1
                else:
                    num_rel[topic] = 0

    return num_rel

def build_trec(trec_data):
    trec = {}
    for line in trec_data:
        q_id, author, doc_id, rank, score, exp = line.split()
        try:
            trec[q_id][doc_id] = score
        except KeyError:
            trec[q_id] = {}
            trec[q_id][doc_id] = score
    return trec

def eval_print(qid, ret, rel, rel_ret,
        prec_at_recalls, avg_prec, prec_at_cutoffs, rec_at_cutoffs, f1_at_cutoffs,
        rp, nDCG, CG = 0, DCG = 0):
    tab = tt.Texttable()
    headers = ["At docs", "Precision", "Recall", "F1"]
    tab.set_deco(tab.HEADER)
    tab.header(headers)
    tab.set_cols_dtype(["t", "f", "f", "f"])
    tab.set_precision(4)
    print("Queryid (num):\t{0}".format(qid))
    print("Total number of documents over all queries")
    print("\tRetrieved:\t{0}".format(ret))
    print("\tRelevant:\t{0}".format(rel))
    print("\tRel_ret:\t{0}".format(rel_ret))
    print("\tCG:\t{0}".format(CG))
    print("\tDCG:\t{0}".format(CG))
    print("Interpolated Recall - Precision Averages:")
    print("\tat 0.00\t\t{0:.4f}".format(prec_at_recalls[0]))
    print("\tat 0.10\t\t{0:.4f}".format(prec_at_recalls[1]))
    print("\tat 0.20\t\t{0:.4f}".format(prec_at_recalls[2]))
    print("\tat 0.30\t\t{0:.4f}".format(prec_at_recalls[3]))
    print("\tat 0.40\t\t{0:.4f}".format(prec_at_recalls[4]))
    print("\tat 0.50\t\t{0:.4f}".format(prec_at_recalls[5]))
    print("\tat 0.60\t\t{0:.4f}".format(prec_at_recalls[6]))
    print("\tat 0.70\t\t{0:.4f}".format(prec_at_recalls[7]))
    print("\tat 0.80\t\t{0:.4f}".format(prec_at_recalls[8]))
    print("\tat 0.90\t\t{0:.4f}".format(prec_at_recalls[9]))
    print("\tat 1.00\t\t{0:.4f}".format(prec_at_recalls[10]))
    print("Average precision (non-interpolated) for all rel docs(averaged over queries)")
    print("\t\t\t{0:.4f}".format(avg_prec))
    print("Average nDCG for all rel docs(averaged over queries)")
    print("\t\t\t{0:.4f}".format(nDCG))
    print("Precision, Recall, F1:")
    
    for row in zip(cutoffs, prec_at_cutoffs, rec_at_cutoffs, f1_at_cutoffs):
        tab.add_row(row)
    s = tab.draw()
    print(s)
    print("R-Precision (precision after R (= num_rel for a query) docs retrieved):")
    print("    Exact:        {0:.4f}".format(rp))

def dcg(relevance_vector):
    dcg_score = 0
    for i, val in enumerate(relevance_vector):
        dcg_score += ((2 ** val) - 1) / math.log(i + 2) # Index starts at 0
    return dcg_score

def main(qrels, trec, print_all_queries):
    qrel = read_file(qrels)
    trec = read_file(trec)
    qrel = build_qrel(qrel)
    trec = build_trec(trec)
    num_rel = build_num_rel(qrel)

    # Variable initialization
    num_topics = 0
    tot_num_ret = 0
    tot_num_rel = 0
    tot_num_rel_ret = 0
    sum_avg_prec = 0.0
    sum_r_prec = 0.0
    sum_nDCG = 0.0
    sum_prec_at_cutoffs = {}
    sum_rec_at_cutoffs = {}
    sum_recall_at_cutoffs = {}
    sum_f1_at_cutoffs = {}
    sum_prec_at_recalls = {}


    # Now let's process the data from trec_file to get results.
    # TODO: Sort the trec based on the topic
    for topic in trec:
        # If no relevant docs, skip topic.
        if topic not in num_rel: continue

        num_topics += 1         # Processing another topic...
        href = trec[topic]      # Processing another topic...
        prec_list = []          # New list of precisions.
        rec_list = []
        num_prec_list = 1000    # Last index is 1000.

        num_ret = 0             # Initialize number retrieved.
        num_rel_ret = 0         # Initialize number relevant retrieved.
        sum_prec = 0            # Initialize sum precision.

        relevance_vector = []

        # Now sort doc IDs based on scores and calculate stats.
        # Note:  Break score ties lexicographically based on doc IDs.
        # Note2: Explicitly quit after 1000 docs to conform to TREC while still
        #        handling trec_files with possibly more docs.

        for doc_id in href:
            num_ret += 1                            # new retrieved doc.

            if doc_id in qrel[topic]:
                rel = 1 if qrel[topic][doc_id] > 0 else 0   # Doc's relevance.
                sum_prec += rel * (1 + num_rel_ret) / num_ret
                num_rel_ret += rel
                # DCG
                relevance_vector.append(qrel[topic][doc_id])
            else:
                relevance_vector.append(0)

            prec_list.append(num_rel_ret / num_ret)
            rec_list.append(num_rel_ret / num_rel[topic])

            if num_ret >= 1000: break

        avg_prec = sum_prec / num_rel[topic]

        # Fill out the remainder of the precision/recall lists, if necessary.

        final_recall = num_rel_ret / num_rel[topic]

        for i in range(num_ret, 1001):
            prec_list.append(num_rel_ret / i)
            rec_list.append(final_recall)

        # Calculate CG
        CG = sum(relevance_vector)
        # Calculate DCG
        DCG = dcg(relevance_vector) 
        # Calculate IDCG
        sorted_relevance_vector = sorted(relevance_vector, reverse=True)
        IDCG = dcg(sorted_relevance_vector)
        # Calculate nDCG
        nDCG = DCG / IDCG
        
        # Now calculate precision at document cutoff levels and R-precision.
        # Note that arrays are indexed starting at 0...
    

        prec_at_cutoffs = []
        rec_at_cutoffs = []
        f1_at_cutoffs = []

        for cutoff in cutoffs:
            prec_at_cutoffs.append(prec_list[cutoff])
            rec_at_cutoffs.append(rec_list[cutoff])

            # To avoid division by zero when calculating F1
            if prec_at_cutoffs[-1] != 0 and rec_at_cutoffs[-1] != 0:
                f1_at_cutoffs.append((2 * prec_at_cutoffs[-1] * rec_at_cutoffs[-1] / (prec_at_cutoffs[-1] + rec_at_cutoffs[-1])))
            else:
                f1_at_cutoffs.append(0)


        # Now calculate R-precision.  We'll be a bit anal here and
        # actually interpolate if the number of relevant docs is not
        # an integer...

        if num_rel[topic] > num_ret:
            r_prec = num_rel_ret / num_rel[topic]
        else:
            int_num_rel = int(num_rel[topic])               # Integer part.
            frac_num_rel = num_rel[topic] - int_num_rel     # Fractional part.

            r_prec = (1 - frac_num_rel) * \
                    prec_list[int_num_rel] + \
                    frac_num_rel * \
                    prec_list[int_num_rel + 1] if frac_num_rel > 0 else prec_list[int_num_rel]

        # Now calculate interpolated precisions...

        max_prec = 0
        for i in range(1000, 0, -1):
            if prec_list[i] > max_prec:
                max_prec = prec_list[i]
            else:
                prec_list[i] = max_prec


        # Finally, calculate precision at recall levels.
        prec_at_recalls = []

        i = 1
        for recall in recalls:
            while i <= 1000 and rec_list[i] < recall:
                i += 1
            if i <= 1000:
                prec_at_recalls.append(prec_list[i])
            else:
                prec_at_recalls.append(0)

        
        # Print stats on a per query basis if requested.
        if print_all_queries:
            eval_print(topic, num_ret, num_rel[topic], num_rel_ret,
                    prec_at_recalls, avg_prec, prec_at_cutoffs, rec_at_cutoffs, f1_at_cutoffs, r_prec, nDCG, CG, DCG)

        # Now update running sums for overall stats.
        tot_num_ret += num_ret
        tot_num_rel += int(num_rel[topic])
        tot_num_rel_ret += num_rel_ret

        for i in range(len(cutoffs)):
            try:
                sum_prec_at_cutoffs[i] += prec_at_cutoffs[i]
            except KeyError:
                sum_prec_at_cutoffs[i] = prec_at_cutoffs[i]

            try:
                sum_rec_at_cutoffs[i] += rec_at_cutoffs[i]
            except KeyError:
                sum_rec_at_cutoffs[i] = rec_at_cutoffs[i]

            try:
                sum_f1_at_cutoffs[i] += f1_at_cutoffs[i]
            except KeyError:
                sum_f1_at_cutoffs[i] = f1_at_cutoffs[i]

        for i in range(len(recalls)):
            try:
                sum_prec_at_recalls[i] += prec_at_recalls[i]
            except KeyError:
                sum_prec_at_recalls[i] = prec_at_recalls[i]

        sum_avg_prec += avg_prec
        sum_r_prec += r_prec
        sum_nDCG += nDCG

    # Now calculate summary stats.
    avg_prec_at_cutoffs = []
    avg_rec_at_cutoffs = []
    avg_f1_at_cutoffs = []
    avg_prec_at_recalls = []

    for i in range(len(cutoffs)):
        avg_prec_at_cutoffs.append(sum_prec_at_cutoffs[i] / num_topics)
        avg_rec_at_cutoffs.append(sum_rec_at_cutoffs[i] / num_topics)
        avg_f1_at_cutoffs.append(sum_f1_at_cutoffs[i] / num_topics)

    for i in range(len(recalls)):
        avg_prec_at_recalls.append(sum_prec_at_recalls[i] / num_topics)

    mean_avg_prec = sum_avg_prec / num_topics
    avg_r_prec = sum_r_prec / num_topics
    avg_nDCG = sum_nDCG / num_topics

    eval_print(num_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret,
            avg_prec_at_recalls, mean_avg_prec, avg_prec_at_cutoffs, avg_rec_at_cutoffs, avg_f1_at_cutoffs,
            avg_r_prec, avg_nDCG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true')
    parser.add_argument('qrels', type = str)
    parser.add_argument('trec', type = str)
    args = parser.parse_args()
    main(args.qrels, args.trec, args.q)
