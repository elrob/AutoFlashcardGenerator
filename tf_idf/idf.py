#!/usr/bin/python

from Doc_Freqs_pkg import Doc_Freqs

relativePath = './tf_idf/document_frequencies/*'

def calc_idfs(list_of_terms):
    # returns a dictionary of terms (keys) and their idf (values)
    import glob
    import cPickle as pickle
     
    # split list of terms by length
    unigrams, bigrams, trigrams, fourgrams, fivegrams = {},{},{},{},{}
    tooLongGrams = {} # potential terms longer than 5 tokens
    for term in list_of_terms:
        if len(term) > 5:
            tooLongGrams[term] = 0
        else:
            (unigrams, bigrams, trigrams, fourgrams, fivegrams)[len(term) - 1][term]=0
    termIDF_dict = {}
    total_docs_in_corpus = 0
    
    # ensure relativePath correct
    assert [folder for folder in glob.glob(relativePath)] 

    for folder in glob.glob(relativePath):
        with open(folder + '/Doc_Freqs_Of'+str(1)+'grams.pickle') as f:
            d = pickle.load(f)
        total_docs_in_corpus += d.number_of_docs

    for n in xrange(1,6):
        current_grams = (unigrams, bigrams, trigrams, fourgrams, fivegrams)[n-1]
        if current_grams:
            for folder in glob.glob(relativePath):
                with open(folder + '/Doc_Freqs_Of'+str(n)+'grams.pickle') as f:
                    d = pickle.load(f)
                if n == 1: # corpus stored unigrams as strings, not tuples
                    for term in current_grams.iterkeys():
                        if term[0] in d.dictOfTermsAndDocFreqs:
                            current_grams[term] += \
                                d.dictOfTermsAndDocFreqs[term[0]]
                else: # longer than unigram. compare tuples directly
                    for term in current_grams.iterkeys():
                        if term in d.dictOfTermsAndDocFreqs:
                            current_grams[term] += \
                                d.dictOfTermsAndDocFreqs[term]
            for term in current_grams.iterkeys():
                termIDF_dict[term] = \
                    float(total_docs_in_corpus)/(1+current_grams[term])
    
    for term in tooLongGrams.iterkeys():
        termIDF_dict[term] = float(total_docs_in_corpus) # assume never found
    return termIDF_dict
            
def calc_idf(term):
    # term can be a tuple if multiword or a string if 1 word
    import glob
    import cPickle as pickle

    
    assert type(term) is tuple, "Terms must be tuples of strings!"

    size = len(term)
    total_docs_in_corpus = 0
    document_frequency = 0
    for folder in glob.glob(relativePath):
        with open(folder + '/Doc_Freqs_Of'+str(size)+'grams.pickle') as f:
            d = pickle.load(f)
        total_docs_in_corpus += d.number_of_docs
        if size == 1: # corpus stored unigrams as strings, not tuples
            if term[0] in d.dictOfTermsAndDocFreqs:
                document_frequency += d.dictOfTermsAndDocFreqs[term[0]]
        else: # longer than unigram. compare tuples directly
            if term in d.dictOfTermsAndDocFreqs:
                document_frequency += d.dictOfTermsAndDocFreqs[term]
    print "Total docs in corpus: ", total_docs_in_corpus
    print "Document frequency: ", document_frequency
    return float(total_docs_in_corpus)/(1+document_frequency)


def create_doc_frequencies_pickles():
    import glob
    import cPickle as pickle
    for folder in glob.glob(relativePath):
        for n in xrange(1,6):
            d = Doc_Freqs()
            d.create_dict_of_terms_and_doc_freqs(folder + '/dictOfSetsOf' \
                                                     + str(n) + 'grams.pickle')
          
            with open(folder + '/Doc_Freqs_Of'+str(n)+'grams.pickle','wb') as f:
                pickle.dump(d,f,-1)
            del d
  
        




# using the Doc_Freqs class is best

# def load_test():
#     import glob
#     import cPickle as pickle
#     for folder in glob.glob('/homes/rps10/rps10Docs/Individual_Project/ScrapingOCW/trainingAndTest/training/*'):
#         for n in xrange(1,6):
#             with open(folder + '/Doc_Freqs_Of'+str(n)+'grams.pickle') as f:
#                 d = pickle.load(f)
#             print n, folder
#             print d.number_of_docs
#             del d

# load_test() 


