from tools.config import Config
import pickle

_config = Config("./config.yml")
_output_dir = _config.get("output_dir")

def write_output(model, query_no, doc_no, rank, score):
    try:
        out = open(_output_dir + model + '.txt', 'a')
        out.write(query_no + ' Bagus ' + doc_no + ' ' +
                rank + ' ' + score + ' Exp\n')
        out.close()
    except Exception as exception:
        print(exception)
