import datetime
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
ps = PorterStemmer()

import json
import sys
import httplib2
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import pickle
import re

class paragraph():
    text = ''
    tokens = []
    stm = []
    tag = ''
    belong_to = ''
    relevancy = ()
    position = 0
    entities = []
    
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

    def get_entities(self):
        DISCOVERY_URL = 'https://language.googleapis.com/$discovery/rest?version=v1beta1'

        http = httplib2.Http()

        credentials = GoogleCredentials.get_application_default().create_scoped(
            ['https://www.googleapis.com/auth/cloud-platform'])
        http=httplib2.Http()
        credentials.authorize(http)

        service = discovery.build('language', 'v1beta1',
                            http=http, discoveryServiceUrl=DISCOVERY_URL)

        service_request = service.documents().analyzeEntities(
            body={
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': self.text,
                }
            })

        response = service_request.execute()

        entity_list = []
        for item in response['entities']:
            temp_entity = {}
            temp_entity['name'] = item['name']
            temp_entity['salience'] = item['salience']
            temp_entity['metadata'] = item['metadata']
            entity_list.append(temp_entity)

        self.entities = entity_list


    def query(self, in_query):
        #tokenizing query
        q = in_query.split()



        
        

class article():

    title = ''
    author = []
    journal = ''
    keywords = []
    sited_freq = 0
    date = datetime.datetime(2000,1,1,1,1,1)

    parts = []
    weight_scheme = {}
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

        #getting basic info
        self.title = root.findall('./info/title')[0].text
        self.author = [x.text for x in root.findall('./info/author')]
        self.keywords = root.findall('./info/keywords')[0].text.split()

        #getting parts
        tags = []
        for node in root:
            tag = ''
            for item in re.split('_| ',node.tag):
                tag += item
                tag += ' '
            tags.append(tag.lower())

        self.parts = self.drop_dup(tags)

        #populating paragraphs
        paras = [x for x in root]
        paras.pop(0)

        paragraphes = []
        for item in paras:
            p = paragraph()
            p.get_content(item, self.title, paras.index(item))
            p.get_entities()
            paragraphes.append(p)

        self.content = paragraphes

    def pickling(self):
        fname = self.title + '.pickle'
        pickle_out = open(fname, 'wb')
        pickle.dump(self, pickle_out)
        pickle_out.close()

    def construct_from_pickle(self, fname):
        pickle_in = open(fname, 'rb')
        temp_article = pickle.load(pickle_in)
        pickle_in.close()

        #print(temp_article.content[0].entities)

        #self = temp_article
        self.title = temp_article.title
        self.author = temp_article.author
        self.journal = temp_article.journal
        self.keywords = temp_article.keywords
        self.sited_freq = temp_article.sited_freq
        self.date = temp_article.date
        self.parts = temp_article.parts
        self.weight_scheme = temp_article.weight_scheme
        self.content = temp_article.content
        
    def get_zonescore(self, in_scheme):
        #scheme is a dictionary
        #types of parts:
            #abstract
            #introduction
            #discussion
            #conclusion
            #remainder

        temp_scheme = {}

        for key, val in in_scheme.items():
            if key.lower() in self.parts:
                temp_scheme[key.lower()] = val

        temp_scheme['remainder'] = in_scheme['remainder']
        self.scheme = temp_scheme


        
#testing
a = article()
a.construct('test1.xml')
a.pickling()

#a.construct_from_pickle('Time-Temperature-Pressure Superposition in Polymer Thickened Liquid Lubricants.pickle')
print(a.content[0].entities)
#print(a.parts)



































