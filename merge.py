from tools.config import Config
import os
import operator

config = Config("./config.yml")
grades_dir = config.get("grades_dir")

bagus_file = [f for f in os.listdir(grades_dir) if f.endswith("Bagus.txt")]
karan_file = [f for f in os.listdir(grades_dir) if f.endswith("Karan.txt")]
monica_file = [f for f in os.listdir(grades_dir) if f.endswith("Monica.txt")]

# Grades = {q_id: {doc_id: relevance1, relevance2, relevance3}}
grades_bagus = {}
grades_karan = {}
grades_monica = {}
grades = {}
not_found = []

# def difference_check():
    # karan_set = set(grades_karan["152601"].keys())        
    # bagus_set = set(grades_bagus["152601"].keys())        
    # monica_set = set(grades_monica["152601"].keys())        
    # diff = bagus_set - monica_set
    # for d in diff:
        # print(d)

def combine_dicts(a, b, op = operator.add):
    return { **a, **b, **{k: op(a[k], b[k]) for k in a.keys() & b}}

def merge():
    global grades_bagus
    global grades_karan
    global grades_monica
    global grades
    global not_found

def store_to_hash(q_id, author, doc_id, relevance):
    global grades_bagus
    global grades_karan
    global grades_monica

    if author == "bagus":
        if q_id in grades_bagus:
            grades_bagus[q_id][doc_id] = [relevance]
        else:
            grades_bagus[q_id] = {}
            grades_bagus[q_id][doc_id] = [relevance]

    if author == "karan":
        if q_id in grades_karan:
            grades_karan[q_id][doc_id] = [relevance]
        else:
            grades_karan[q_id] = {}
            grades_karan[q_id][doc_id] = [relevance]

    if author == "monica":
        if q_id in grades_monica:
            grades_monica[q_id][doc_id] = [relevance]
        else:
            grades_monica[q_id] = {}
            grades_monica[q_id][doc_id] = [relevance]

def split_line(line):
    try:
        q_id, author, doc_id, relevance = line.split()
        data = {q_id: {doc_id: relevance}}
        store_to_hash(q_id, author.lower(), doc_id, relevance)
    except Exception as e:
        print(e)

def write_to_text(name, data):
    with open(name + ".txt", "w") as q:
        for key in data:
            string = "{0}\tBagus\t{1}\t{2}\n".format(name, key, ",".join(data[key]))
            q.write(string)

for bagus, karan, monica in zip(bagus_file, karan_file, monica_file):
    with open(grades_dir + bagus, "r") as b, open(grades_dir + karan, "r") as k, open(grades_dir + monica, "r") as m:
        text_bagus = b.read()
        text_karan = k.read()
        text_monica = m.read()

    lines_bagus = text_bagus.split("\n")
    lines_karan = text_karan.split("\n")
    lines_monica = text_monica.split("\n")

    for line_bagus, line_karan, line_monica in zip(lines_bagus, lines_karan, lines_monica):
        split_line(line_bagus)
        split_line(line_karan)
        split_line(line_monica)

grades_152601 = grades_bagus["152601"]
grades_152601 = combine_dicts(grades_152601, grades_karan["152601"])
grades_152601 = combine_dicts(grades_152601, grades_monica["152601"])

grades_152602 = grades_bagus["152602"]
grades_152602 = combine_dicts(grades_152602, grades_karan["152602"])
grades_152602 = combine_dicts(grades_152602, grades_monica["152602"])

write_to_text("152601", grades_152601)
write_to_text("152602", grades_152602)
