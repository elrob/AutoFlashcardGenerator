#!/usr/bin/python

class Doc_Freqs():
    # a class with two attributes:
    # number_of_docs: the number of documents in this part of the corpus
    # dictOfTermsAndDocFreqs: a dictionary with terms as keys and the 
    #                         number of documents they appear in as values.

    def create_dict_of_terms_and_doc_freqs(self,dictOfSetsPath):
         with open(dictOfSetsPath) as f:
             import cPickle as pickle
             dictOfSets = pickle.load(f)
         self.number_of_docs = len(dictOfSets)
         print "Path: ", dictOfSetsPath
         print "Number of docs: ", self.number_of_docs
         fullSet = set().union(*dictOfSets.itervalues())
         self.dictOfTermsAndDocFreqs = {}
         for corpus_term in fullSet:
                freq = sum(1 for wordset in dictOfSets.itervalues() if corpus_term in wordset)
                self.dictOfTermsAndDocFreqs[corpus_term] = freq
