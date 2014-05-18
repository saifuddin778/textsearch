from textblob import TextBlob
from collections import Counter
from compiler.ast import flatten
import ast
import json
import operator
import shelve


class TextSearch:
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

    def tokenize(self):
        """tokenizes all the documents by keeping their nouns in"""
        for a in self.dataset:
            if len(a):
                if type(a) is list:
                    self.index_present = True
                    if len(a) == 2:
                        a = a[1]
                        new_item = [b[0] for b in TextBlob(a).tags if b[1] in ['NN', 'NNS']]
                    else:
                        continue
                elif type(a) is str:
                    self.index_present = False
                    new_item = [b[0] for b in TextBlob(a).tags if b[1] in ['NN', 'NNS']]
            else:
                continue
            
            self.tokenized_dataset.append(new_item)

        return self.tokenized_dataset


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
            for k_, v_ in sorted(ast.literal_eval(json.dumps(Counter(' '.join(flatten(data)).split(' ')))).iteritems(), key=lambda (k_,v_): (v_,k_), reverse=True):
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
        print "%d words added to the search hash" % len(flatten(hash_.values()))
        

    #loads and returns the generated hashes instance
    def load_hashes(self):
        """loads and returns the generated hashes instance"""
        hash_ = shelve.open('search_db.bin')
        return hash_

    #loads and returns the histogram instance
    def load_histogram(self):
        """loads and returns the histogram instance"""
        histogram_ = shelve.open('data_histo.bin')
        return histogram_


    #performs the search over existing set of documents based on the input query
    def lookup(self, keyword, individual=False):
        yield_docs = lambda x: {'index': x, 'doc': self.dataset[x][1], 'doc_id': self.dataset[x][0]} if self.index_present else {'index': x, 'doc': self.dataset[x]} 

        keyword = keyword.split(' ')
        #hash_ = self.load_hashes()
        hash_ = self.hash__
        
        results_ = []
        
        if len(keyword) == 1:
            for a in keyword:
                try:
                    results_.append(hash_[a.encode('utf-8')])
                except:
                    continue
            
            results_ = map(yield_docs, flatten(results_))

        elif len(keyword) > 1:
            for a in keyword:
                try:
                    results_.append(hash_[a.encode('utf-8')])
                except:
                    continue
                
            if individual:
                results_ = sorted(map(yield_docs, flatten(results_)), reverse=True)
            else:
                int_results_ = list(set.intersection(*map(set,results_)))
                if len(int_results_):
                    results_ = map(yield_docs, int_results_)
                else:
                    results_ = sorted(map(yield_docs, flatten(results_)), reverse=True)

        return results_

