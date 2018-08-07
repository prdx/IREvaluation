import argparse

qrel = {}
trec = {}

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
    global qrel
    for line in qrel_data:
        (q_id, author, doc_id, relevance) = line.split("\t")
        try:
            qrel[q_id][doc_id] = relevance
        except KeyError:
            qrel[q_id] = {}
            qrel[q_id][doc_id] = relevance 

def build_trec(trec_data):
    global trec
    
    for line in trec_data:
        (q_id, author, doc_id, rank, score, exp) = line.split()
        try:
            trec[q_id][doc_id] = score
        except KeyError:
            trec[q_id] = {}
            trec[q_id][doc_id] = score


def main(qrels, trec, q):
    qrel = read_file(qrels)
    trec = read_file(trec)
    build_qrel(qrel)
    build_trec(trec)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true')
    parser.add_argument('qrels', type = str)
    parser.add_argument('trec', type = str)
    args = parser.parse_args()
    main(args.qrels, args.trec, args.q)

