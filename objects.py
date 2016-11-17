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
import operator

class paragraph():


	def __init__(self):
		text = ''
		tokens = []
		stm = []
		tag = ''
		belong_to = ''
		position = 0
		entities = []

		temp_rlv = 0.0
	
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
		raw_tokens = word_tokenize(s)
		self.tokens = [x.lower() for x in raw_tokens]

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


	def query_para(self, q_content, q_tag, art_vars, q_scheme):

		#scores to use
		para_rlv = 0.0

		title_rlv = art_vars['title_rlv']
		keyw_rlv = art_vars['keyw_rlv']
		abs_t_rlv = art_vars['abs_t_rlv']
		abs_e_rlv = art_vars['abs_e_rlv']

		tag_rlv = 0.0
		subt_rlv = 0.0
		token_rlv = 0.0
		entity_rlv = 0.0

		#possible tags
		possible_tags = ['abstract',
						 'introduction',
						 'discussion',
						 'conclusions']

		#processing

		#tag
		tag_tokens = [x.lower() for x in self.tag.split()]

		for token in q_tag:
			if token in tag_tokens:
				tag_rlv += q_scheme['tag_rlv']

		#subt
		for token in q_content:
			if token in tag_tokens:
				subt_rlv += q_scheme['subt_rlv']

		#get weight
		weight = q_scheme['remainder']
		#print(self.tag)
		if self.tag.lower() in possible_tags:
			weight = q_scheme[self.tag.lower()]
			#print('w')

		#token & entity
		for token in q_content:

			#token
			if token in self.tokens:
				token_rlv += q_scheme['token_rlv'] * weight

			#entities
			for entity in self.entities:
				entities_name_token = [x.lower() for x in entity['name'].split()]
				if token in entities_name_token:
					temp_entity_score = q_scheme['entity_rlv'] * float(entity['salience'])
					entity_rlv += temp_entity_score * weight

		#add up score
		#havn't normalized the scores to compensate for missing tags
		para_rlv = title_rlv + keyw_rlv + abs_t_rlv + abs_e_rlv + tag_rlv + subt_rlv + token_rlv + entity_rlv
		self.temp_rlv = para_rlv
		#print(para_rlv)
		#print(tag_rlv)
		#print(subt_rlv)
		#print(weight)
		#print('token: ', token_rlv)
		#print('entity: ', entity_rlv)
		



class query():

	def __init__(self):
		#input text
		text = ''
		tokens = []
		content_tokens = []
		tag_tokens = []

		# forprocessing
		q_scheme = {}

	#separate content tags from content in query
	def separate(self):
		possible_tags = ['abstract',
						 'introduction',
						 'discussion',
						 'conclusions']
		t_tokens = []
		c_tokens = []
		for token in self.tokens:
			if token in possible_tags:
				t_tokens.append(token)
			else:
				c_tokens.append(token)

		self.tag_tokens = t_tokens
		self.content_tokens = c_tokens
		#print(self.tag_tokens, self.content_tokens)

	#actual process
	def in_query(self, in_text):
		self.text = in_text
		self.tokens = [x.lower() for x in in_text.split()]
		self.separate()

	def get_scheme(self, in_scheme):
		self.q_scheme = in_scheme

	#getting score for abstract comparison
	def process_abstract(self, in_article):
		token_rlv = 0.0
		entity_rlv = 0.0

		abs_exists = False

		#getting abstract
		abs = paragraph()
		for p in in_article.content:
			if p.tag.lower() == 'abstract':
				abs = p
				abs_exists = True

		#abstract rlv
		if abs_exists:
			for token in self.content_tokens:
				#abstract tokens
				if token in abs.tokens:
					token_rlv += self.q_scheme['abs_rlv']

				#abstract entities
				for entity in abs.entities:
					entities_name_token = [x.lower() for x in entity['name'].split()]
					if token in entities_name_token:
						temp_entity_score = self.q_scheme['entity_rlv'] * float(entity['salience'])
						entity_rlv += temp_entity_score

		#returning results
		return token_rlv, entity_rlv

	#process individual articles
	def process_article(self, in_article):
		title_rlv = 0.0
		keyw_rlv = 0.0
		abs_t_rlv = 0.0
		abs_e_rlv = 0.0

		title_tokens = [x.lower() for x in in_article.title.split()]

		for token in self.content_tokens:
			if token in title_tokens:
				title_rlv += self.q_scheme['title_rlv']

			if token in in_article.keywords:
				keyw_rlv += self.q_scheme['keyw_rlv']

		abs_t_rlv, abs_e_rlv = self.process_abstract(in_article)

		return title_rlv, keyw_rlv, abs_t_rlv, abs_e_rlv

	#article level comparison
	def loop_articles(self, in_articles):
		for article in in_articles:
			#need dynamic scheme

			title_rlv, keyw_rlv, abs_t_rlv, abs_e_rlv = self.process_article(article)
			article_vars = {}
			article_vars['title_rlv'] = title_rlv
			article_vars['keyw_rlv'] = keyw_rlv
			article_vars['abs_t_rlv'] = abs_t_rlv
			article_vars['abs_e_rlv'] = abs_e_rlv
			#feed vars above to each para object in article
			for para in article.content:
				para.query_para(self.content_tokens, self.tag_tokens, article_vars, self.q_scheme)

	#the this a temperary solution
	#taking up to much memmory space and too slow
	def rank_para(self, in_articles):

		self.loop_articles(in_articles)
		
		#getting set of paras
		p_set = {}

		for article in in_articles:
			for para in article.content:
				score = para.temp_rlv
				#print(score)
				p_set[score] = para

		#print(p_set)

		#ranking
		sorted_p = sorted(p_set.items(), key=operator.itemgetter(0), reverse=True)

		#print(sorted_p)
		return sorted_p




		
		

class article():

	def __init__(self):
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
		#self.journal = temp_article.journal
		self.keywords = temp_article.keywords
		#self.sited_freq = temp_article.sited_freq
		#self.date = temp_article.date
		self.parts = temp_article.parts
		#self.weight_scheme = temp_article.weight_scheme
		self.content = temp_article.content
	
	#get rid of this function    
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

#constructing article
a = article()
#a.construct('test1.xml')
#a.pickling()
a.construct_from_pickle('Time-Temperature-Pressure Superposition in Polymer Thickened Liquid Lubricants.pickle')
#print(a.content[0].entities)
art_list = [a]

#creating query
q = query()
q.in_query('lubrication pressure principle')

#q_scheme
sch = {'title_rlv':5,
	   'keyw_rlv':4,
	   'abs_rlv':3,
	   'tag_rlv':3,
	   'subt_rlv':3,
	   'token_rlv':3,
	   'entity_rlv':3,
	   'abstract':1,
	   'introduction':1,
	   'discussion':4,
	   'conclusions':4,
	   'remainder':5,}
q.get_scheme(sch)

#querying
result = q.rank_para(art_list)
print(result[0][0])
print(result[0][1].text)





































