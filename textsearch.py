import sys
import os
sys.dont_write_bytecode = True
from textblob import TextBlob
from collections import Counter
from string import translate
import ast
import json
import operator
import shelve


class textsearch(object):
    """define a new hash based document retrieval system"""
    
    def __init__(self, dataset, histogram=False):
        """invokes the process with the dataset"""
        self.dataset = dataset
        self.data_count = len(dataset)
        self.tokenized_dataset = []
        if histogram:
            self.create_histo = 1
            self.histogram_ = {}
        else:
            self.create_histo = 0
        self.create_hash()
        self.hash__ = shelve.open('search_db.bin')

    translate_ = lambda self, n: n.translate(None, '`~!{}[]\|/\n\t:;"<>?,.@#$%^&*()-_+=')

    def flatten(self, x, y):
        for i, a in enumerate(x):
            if type(x[i]) == type([]):
                self.flatten(x[i], y)
            else:
                y.append(x[i])
        return y

    def tokenize(self):
        """tokenizes all the documents by keeping their nouns in"""
        for a in self.dataset:
            if len(a):
                #ids are provided along with the documents
                if type(a)  == type(()) or type([]):
                    self.index_present = True
                    if len(a) == 2:
                        a = a[1]
                        new_item = [b[0] for b in TextBlob(self.translate_(a)).tags if b[1] in ['NN', 'NNS']]
                    else:
                        continue
                #no ids are provided, so use indices
                elif type(a) is str:
                    self.index_present = False
                    new_item = [b[0] for b in TextBlob(self.translate_(a)).tags if b[1] in ['NN', 'NNS']]
            else:
                continue
            self.tokenized_dataset.append(new_item)
        return self.tokenized_dataset

    #generates the hash
    def create_hash(self):
        """generates the hashes and histogram for the submitted data"""
        data = self.tokenize()
        #building the hash
        if len(data):
            hash_ = {}
            for _id, sentence in enumerate(data):
                for _, word in enumerate(list(set(sentence))):
                    if hash_.get(word) is None:
                        hash_[word] = {}
                    hash_[word][len(hash_[word])+1] = _id
        
        #removing unnecessary indices
        for k,v in hash_.iteritems():
            hash_[k] = v.values()
        #if histogram needs to be created
        if self.create_histo:
            for k_, v_ in sorted(ast.literal_eval(json.dumps(Counter(' '.join(self.flatten(data,[])).split(' ')))).iteritems(), key=lambda (k_,v_): (v_,k_), reverse=True):
                self.histogram_[k_] = v_
            #persist the histogram
            histo_file_ = shelve.open('data_histo.bin')
            for k, v in self.histogram_.iteritems():
                histo_file_[k] = v
            histo_file_.close()
        #persist the hash
        hash_file_ = shelve.open('search_db.bin')
        for key, value in hash_.iteritems():
            hash_file_[key] = value
        hash_file_.close()
        print "all done"
        print "%d unique words added to the lookup table" % len(self.flatten(hash_.values(), []))
        

    #loads and returns the generated hashes instance
    def load_hashes(self):
        """loads and returns the generated hashes instance"""
        hash_ = shelve.open('search_db.bin')
        return hash_

    #loads and returns the histogram instance
    def load_histogram(self):
        histogram_ = shelve.open('data_histo.bin')
        return histogram_
    
    #performs the search over existing set of documents based on the input query
    def lookup(self, keyword, individual=False):
        yield_docs = lambda x: {'index': x, 'doc': self.dataset[x][1], 'doc_id': self.dataset[x][0]} if self.index_present else {'index': x, 'doc': self.dataset[x]} 
        keyword = keyword.split(' ')
        hash_ = self.hash__
        results_ = []
        #if the query is of a single keyword, then this world still has wonderful people in it.
        if len(keyword) == 1:
            for a in keyword:
                try:
                    results_.append(hash_[a.encode('utf-8')])
                except:
                    continue
            results_ = map(yield_docs, self.flatten(results_, []))
        #else, we have more precise people.
        elif len(keyword) > 1:
            for a in keyword:
                try:
                    results_.append(hash_[a.encode('utf-8')])
                except:
                    continue
            if individual:
                results_ = sorted(map(yield_docs, self.flatten(results_, [])), reverse=True)
            else:
                #okay, so now the point is that we should always look into
                #the intersection, because in any way, the documents containing
                #all the concepts are definitely the one of interest to the users.
                int_results_ = list(set.intersection(*map(set,results_)))
                if len(int_results_):
                    results_ = map(yield_docs, int_results_)
                else:
                    #if there is no intersection retrieved, then simple return the matches.
                    results_ = sorted(map(yield_docs, self.flatten(results_, [])), reverse=True)
        return results_
