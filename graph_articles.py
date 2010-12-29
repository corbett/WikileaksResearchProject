#!/usr/bin/env python

# Dependencies
# 1. NLTK and training data
# used for splitting into sentences in more robust way than regex
# -INSTALL:
# sudo python easy_install nltk
# python
# import nltk
# >> nltk.downloader()
# ...download punkt data from gui
# 2. Beautiful soup
# I don't use instapaper's parser but write my own simple one which 
# relies on Beautiful Soup
# -INSTALL:
# sudo easy_install beautifulsoup
# 3. pygraph
# used to create graph of connections between files
# -INSTALL:
# sudo easy_install python-graph-core
# sudo easy_install python-graph-dot
# 4. Tool to visualize dot files
# used to visualize the created graph
# -INSTALL:
# I used graphviz.app which has a dmg to install http://www.graphviz.org/

import os,sys,codecs
from BeautifulSoup import *
# Import pygraph, use for visualizing connections
from pygraph.classes.graph import graph
from pygraph.readwrite.dot import write
import nltk.data
from nltk import word_tokenize
from collections import defaultdict

class Parser:
    def __init__(self):
        pass
    def parse(self,data):
        data=BeautifulSoup(data)
        title=''
        contents=''
        try:
            title=data.title.string
            contents=re.sub('\n','\\\\n',self.extract_strings(data.body))
        except Exception,e:
            pass
        return title,contents
    def extract_strings(self,elem):
        contents=''
        if isinstance(elem, Tag):
            contents+=''.join(map(self.extract_strings,elem.contents))
            return contents 
        else:
            return elem
links=defaultdict(list)
# Parser and tokenizer used to split docs into sentences
parser=Parser()
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
doc_map=codecs.open('../wl_article_connections.dict','w','utf-8')
interest_map=defaultdict(lambda:defaultdict(lambda: 0))
interests=['assange','Assange','Schmitt','schmitt','Clinton','clinton','Obama','obama','Rape','rape','Wikileaks','wikileaks']

# Graph creation, linking any documents which contain the same sentences
gr = graph()
# Mapping sentences to docs which contain them 
for i,name in enumerate(os.listdir('.')):
    # We'll represent docs by numbers instead of names to keep things clear
    doc_map.write(u'%d\t%s\n' % (i,name))
    doc=codecs.open(name).read()
    try:
        title,doc=parser.parse(doc)
        sentences = tokenizer.tokenize(doc.strip())
        for sent in sentences:
            #TODO: figure out utf-8 eqv. of map(str.lower,words) or use nltk normalizer
            words=dict.fromkeys(word_tokenize(sent))
            for thing in interests:
                if words.has_key(thing):
                    interest_map[doc][thing]=1
            links[sent]+=[i]
    except Exception,e:
        continue

#we are ready to print out thing of interest stats 
# TODO: write to a file I am in a hurry
print 'Out of',i,len(interest_map.keys())
for thing in interests:
    print thing
    print sum(map(lambda d:d[thing],interest_map.values()))

# I have this list of banned characters as the parser (above) isn't all that talented at getting rid of javascript/html at all times. I assume if a sentence has these characters it is one of the afforementioned
banned_chars=['<','>','\.js','=','+','{','}','&','_','(',')','#','`','http'] #TODO change this to a regexp
matching_sents={}
connection_count=defaultdict(lambda: 0)
for sent,docs in links.items():
    banned=False
    for char in banned_chars:
        if char in sent: banned=True
    if banned: continue
    matching_sents[sent]=1
    for d1 in docs:
        for d2 in docs:
            if d1!=d2:
                if not gr.has_node(d1):
                    gr.add_node(d1)
                if not gr.has_node(d2):
                    gr.add_node(d2)                
                if gr.has_edge((d1,d2)): continue
                gr.add_edge((d1,d2))
                connection_count[d1]+=1
                connection_count[d2]+=1

# Just for debugging the number of matching sentences is printed
print len(matching_sents.keys())

# These will be the nodes sorted in descending order of the number of connections they have. format <node number> tab <number connections>
most_connections=open('../most_connections.dict','w')
connections=connection_count.items() 
connections.sort(lambda x,y:cmp(y[1],x[1]))
connections=map(lambda x:'%s\t%d' % (x[0],x[1]),connections)
most_connections.write('\n'.join(connections))

# Finally writing out the graph
dot = write(gr)
outfile = codecs.open('../wl_article_connections.dot','w','utf-8') # visualize with gv python module, or write dotfile and visualize with your favorite app (graphviz.app)
outfile.write(dot)
