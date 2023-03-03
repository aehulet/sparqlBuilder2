
class QueryRecord:
    title = ""
    query = ""
    index = 0
    def __init__(self, title, query):
        self.title = title
        self.query = query

    def get_query(self):
        return self.query

    def set_index(self, num):
        self.index = num
