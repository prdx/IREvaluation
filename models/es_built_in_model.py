from tools.es import search

class BuiltInModel(object):
    def query(self, keywords = ""):
        return search(keywords)
