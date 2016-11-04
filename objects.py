import datetime

class paragraph():
    #represents a paragraph
    
    def __init__(self):
        text = ''
        stemmed = []
        in_article = ''
        in_part = ''
        relevancy = ()
        i_in_part = 0
        i_in_article = 0

    #populating paragraph object from a txt file with only 1 paragraph in it
    #paragraph info is specified in txt file
    #for testing porpose
    def from_sep_txt(self, fname):
        f = open(fname, 'r'):
            self.text = ''
        f.close()

    #populate paragraph object from article level
    #inputing txt from article class
    def from_article(self, article):
        pass

    #stemming text into key words with no internal logic
    def stem(self):
        pass

    #stemming text into key words with no internal logic
    def stem_logic(self):
        pass

    #generate a tuple: (relevancy score, query str)
    def query(self, query):
        pass


class part():
    #represents a certain part in article such as abstract or conclusion
    #list possible parts here:
        #TBD
    
    def __init__(self):
        part_type = ''
        list_para = []
        subtitle = ''
        in_article = ''
        i_in_article = 0
        weight = 0.0

    #populate part object from individual article objects
    #for testing porpose
    def from_para(self, para):
        pass

    #populating part object from article level
    def from_article(self, article):
        pass

    #set weight of part according to article level weight schema
    def set_weight(self):
        pass

class block():
    #represents a part of the article on a spedific topic
    
    def __init__(self):
        list_para = []
        subtitle = ''
        in_article = ''
        i_in_article = 0
        weight = 0.0

    #populate part object from individual article objects
    #for testing porpose
    def from_para(self, para):
        pass

    #populating part object from article level
    def from_article(self, article):
        pass

    #set weight of part according to article level weight schema
    def set_weight(self):
        pass


class article():
    #representing a complete article

    def __init__(self):
        title = ''
        author = []
        journal = ''
        #potential author/journal rating & objects

        list_part = []
        weight_schema_part = {}
        sited_freq = 0
        date = datetime.datetime()

    #construct article object from paragraphs
    #for test porpose
    def from_para():
        pass

    #construct article and its part and paragraphes
    #from file containing complete article
    def from_article():
        pass

    #summarize article somehow
    def summary():
        pass

class query():
    #represent a query & its results

    def __init__(self):
        query_str = ''
        stemmed = []

    def input_query(self, in_str):
        pass

class query_result():
    #represent the result of a query

    def __init__(self):
        q = query()
        result = []
        #result is a ranked list of paragraph objects

    #get context of a resulted paragraph
    def get_context():
        pass


#importing
def construct_para():
    pass

def construct_art():
    pass

def pickling():
    pass

def store_to_db():
    pass

#querying
def querying():
    pass

#create a customized dictionary for stemming
def create_dict():
    pass
    
        
        















































