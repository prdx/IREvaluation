from models.es_built_in_model import BuiltInModel
from tools.score_writer import write_output
import re

query_list = {}

def run_built_in():
    print("Processing: built in model")
    built_in = BuiltInModel()
    for key in query_list:
        results = built_in.query(query_list[key])['hits']['hits']
        rank = 1
        for result in results:
            write_output(
                    model = 'es',
                    query_no = str(key),
                    doc_no = result['_id'],
                    rank = str(rank),
                    score = str(result['_score']))
            rank += 1

def build_query_list():
    key_val = []
    query_list = {}
    try:
        f = open('./query_list.txt', 'r').read()
        f = f.split('\n')

        for q in f:
            key_val = re.split('\s{3}', q.strip())
            if len(key_val) == 2:
                query_list[key_val[0]] = key_val[1]

        return query_list
    except Exception as exception:
        print(exception)

if __name__ == '__main__':
    query_list = build_query_list()
    run_built_in()

