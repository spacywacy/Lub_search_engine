import datetime
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
ps = PorterStemmer()

class paragraph():
    
    def __init_(self):
        text = ''
        tokens = []
        stm = []
        tag = ''
        belong_to = ''
        relevancy = ()
        position = 0

    #using nltk.stem.PorterStemmer
    def stemming(self):
        stemmed = []
        for t in self.tokens:
            stemmed_word = ps.stem(t)
            stemmed.append(stemmed_word)
            
        self.stm = stemmed

    def get_content(self, in_node, in_title, in_pos, method='porter'):
        #getting basic info
        self.tag = in_node.tag
        self.belong_to = in_title
        self.position = in_pos

        #getting raw text
        raw_list = in_node.text.split()
        s = ''
        for item in raw_list:
            s += item
            s += ' '

        self.text = s

        #tokenizing
        self.tokens = word_tokenize(s)

        #stem
        if method == 'porter':
            self.stemming()
        else:
            pass

    def query(self):
        pass
        
        

class article():

    def __init__(self):
        title = ''
        author = []
        journal = ''
        keywords = []
        sited_freq = 0
        date = datetime.datetime(2000,1,1,1,1,1)

        parts = []
        weight_schema = {}
        content = []

    def drop_dup(self, in_list):
        out_list = []
        for item in in_list:
            if not (item in out_list):
                out_list.append(item)

        return out_list

    def construct(self, fname):
        tree = ET.parse(fname)
        root = tree.getroot()

        #getting basic infot
        self.title = root.findall('./info/title')[0].text
        self.author = [x.text for x in root.findall('./info/author')]
        self.keywords = root.findall('./info/keywords')[0].text.split(',')

        #getting parts
        tags = [x.tag for x in root]
        self.parts = self.drop_dup(tags)

        #populating paragraphs
        paras = [x for x in root]
        paras.pop(0)

        paragraphes = []
        for item in paras:
            p = paragraph()
            p.get_content(item, self.title, paras.index(item))
            paragraphes.append(p)

        self.content = paragraphes
        
        
#testing
a = article()
a.construct('test1.xml')



































