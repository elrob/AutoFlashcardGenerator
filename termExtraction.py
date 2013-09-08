#!/usr/bin/python

from __future__ import division
import nltk, re, pprint, itertools, math
from collections import Counter
from tidyAndTokenizeTools import tidyAndTokenize
from tidyAndTokenizeTools.word_check import is_clean_word

from nltk.stem import WordNetLemmatizer
WN_LEMMATIZER = WordNetLemmatizer()

# Note: can't simplify N|NP to N.* because there is a NUM tag

# 7) BEST PERFORMING CHUNK GRAMMAR
SIMPLIFIED_GRAMMAR = r""" 
         NounPhrase: {(<POS|ADJ|N|NP>+|(<POS|ADJ|N|NP>*<P>?)<POS|ADJ|N|NP>*)<N|NP>} 
                     {<N|NP>}
         """

# # 2)
# SIMPLIFIED_GRAMMAR = r""" 
#          NounPhrase: {<.*>+}          # Chunk everything
#                      }<V|V.|P>+{      # Chink sequences of Verbs/Prepositions
#          """


NP_PARSER = nltk.RegexpParser(SIMPLIFIED_GRAMMAR)


def tokenize(filepath):
    # return a list of sentences. Each sentence is a list of word tokens.
    return tidyAndTokenize.TidyTokenizedText(filepath).get_tidy_input_tokens()

def stanford_tag(tokens):
    from stanford_tagger import stanford
    st_tagger = stanford.POSTagger('./stanford_tagger/stanford-postagger-2013-04-04/models/wsj-0-18-bidirectional-nodistsim.tagger','./stanford_tagger/stanford-postagger-2013-04-04/stanford-postagger.jar')

    return st_tagger.batch_tag(tokens)


def tag(tokens):
    # tokens is a list of sentences. Each sentence is a list of word tokens.
    return nltk.tag.batch_pos_tag(tokens)

def simplify_tags(tagged_tokens):
    # tagged tokens is a list of sentences. 
    # Each sentence is a list of (word, tag) tuples.
    from nltk.tag.simplify import simplify_wsj_tag
    
    def simplify_tag(tag):
        # Keep POS tag as it is useful: many terms contain possessive: "'s"
        if tag.lower() == 'pos':
            return 'POS'
        else:
            simple_wsj_tag = simplify_wsj_tag(tag)
        if not simple_wsj_tag:
            # Convert '' tags to 'EMPTY' as RegexpParser doesn't like the 
            # empty wsj simplified tag.
            return 'EMPTY'
        else:
            return simple_wsj_tag


    return [[(word, simplify_tag(tag)) for word, tag in sent] for sent in tagged_tokens]
    

def noun_phrase_chunks(simple_tagged_tokens):
    # simple_tagged_tokens is a list of sentences.
    # Each sentence is a list of (word, tag) tuples using simple wsj tags.

    def traverse(t, np_list):
        # A tree traversal function for extracting NP chunks in the parsed tree.
        # t has type tree and so does its children.
        try:
            t.node
        except AttributeError:
            return
        else:
            if t.node == 'NounPhrase': 
                # t.leaves(): appends only the noun phrase as a list of strings 
                np_list.append(t.leaves())
            else:
                for child in t:
                    traverse(child, np_list)


    noun_phrase_chunks_with_tags = []
    for sent in simple_tagged_tokens:
        # a complete tree is returned after parse which is traversed 
        traverse(NP_PARSER.parse(sent),noun_phrase_chunks_with_tags) 
    # noun_phrase_chunks_with_tags is now a list of noun phrase chunks
    # which are lists of word, tag tuples.  
    return noun_phrase_chunks_with_tags



def clean_noun_phrase_chunks(noun_phrase_chunks):
    # get rid of stop list items and individual characters
    # noun_phrase_chunks is a list of noun phrases
    # each noun phrase is a list of word, tag tuples
    
    from string import punctuation 
    # '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    def is_clean_word_tag_tuple(word_tag_tuple):
        word, tag = word_tag_tuple
        return is_clean_word(word)

    def clean_noun_phrase(np):
        # np is a list of words in a noun phrase
              
        clean_np = filter(is_clean_word_tag_tuple, np)
        return clean_np

    
    noun_phrase_chunks_clean = filter(None, (clean_noun_phrase(np) \
                                                 for np in noun_phrase_chunks)) 
    return noun_phrase_chunks_clean   


def get_nested_noun_phrase_chunks(noun_phrase_chunks):
    # grabs any nested noun phrases
    # helpful for when original noun phrase includes tokens
    # which shouldn't really be part of the noun-phrase 
    # e.g. [('use', 'V'), ('firewalls', 'N')] should just be 'firewalls'
    
    def is_nounphrase(tagged_phrase):
        # Determine whether a tagged phrase matches the
        # noun-phrase regular expression tag sequence
        for subtree in NP_PARSER.parse(tagged_phrase).subtrees():
            if subtree.node == 'NounPhrase':
                return True
        return False

    from nltk.util import ingrams

    nested_noun_phrase_chunks = []
    for np in noun_phrase_chunks:
        for ngramSize in xrange(len(np)-1,0,-1):
            for ngram in ingrams(np,ngramSize):
                if is_nounphrase(ngram):
                    nested_noun_phrase_chunks.append(list(ngram))
    return nested_noun_phrase_chunks

def append_nested_noun_phrases(noun_phrase_chunks):
    nested_noun_phrases = get_nested_noun_phrase_chunks(noun_phrase_chunks)
    extended_noun_phrases = noun_phrase_chunks + nested_noun_phrases
    return extended_noun_phrases

def chunks_without_tags(noun_phrase_chunks):
    # filter out tags
    return [[word for word, tag in np] for np in noun_phrase_chunks]



def lemmatize(noun_phrase_chunks,verbose = False):
    # print the changes that lemmatization makes
    # note: to match tidyAndTokenize corpus tokens, only non-stopwords
    #       should be lemmatized. 
    if verbose:
        for change in set((word,WN_LEMMATIZER.lemmatize(word.lower())) for word in itertools.chain.from_iterable(noun_phrase_chunks) if word.lower() != WN_LEMMATIZER.lemmatize(word.lower())):
            print change
    return [[WN_LEMMATIZER.lemmatize(word.lower()) for word in np] for np in noun_phrase_chunks]


def calc_c_values(counts):
    # counts is type <class 'collections.Counter'>
    max_length = max(len(key) for key in counts.keys())

    def is_nested_in(np, longer_np):
        for i in xrange(0,len(longer_np)-len(np)+1):
            if longer_np[i:i+len(np)] == np:
                # print np, "FOUND IN", longer_np
                return True
        return False

    def terms_np_is_nested_in(noun_phrase):
        return [longer_np for longer_np in counts.keys() \
                if len(longer_np) > len(noun_phrase) and \
                is_nested_in(noun_phrase,longer_np)]

    def get_f(term):
        return math.log(counts[term],2) # modified from original Frantzi C-value method

    def neg_part(noun_phrase):
        terms_containing_noun_phrase = terms_np_is_nested_in(noun_phrase)
        # this is already a set (no duplicates possible)

        sum_of_frequencies = sum(get_f(term) for term in \
                                 terms_containing_noun_phrase)

        if not terms_containing_noun_phrase:
            return 0
        else: # redundant else
            return float(sum_of_frequencies)/len(terms_containing_noun_phrase)
            
    def c_value(noun_phrase):
        # includes modifications from the original Frantzi c-value method.
        length = len(noun_phrase)

        if length == max_length:
            return (1+math.log(length,2))*(get_f(noun_phrase))
        else: # length < max_length
            return (1+math.log(length,2))*(get_f(noun_phrase) - neg_part(noun_phrase))
    
    return sorted(((np,c_value(np)) for np in counts.keys()),\
                  key = lambda pair: pair[1],\
                  reverse = True)

def get_term_idf_dict(term_tuples):
    from tf_idf.idf import calc_idfs
    import tf_idf
    import sys
    sys.modules['Doc_Freqs_pkg'] = tf_idf.Doc_Freqs_pkg
    return calc_idfs(term_tuples)


def get_all_n_grams(tokens,min_n,max_n):
    from nltk.util import ngrams
    all_n_grams = []
    for sent in tokens:
        for n in xrange(min_n,max_n+1):
            all_n_grams += ngrams(sent,n)
    all_n_grams = [ngram for ngram in all_n_grams if ngram] # remove empty n-grams
    return all_n_grams

def clean_all_n_grams(n_grams):
    clean_n_grams = [filter(lambda word: is_clean_word(word),ngram) for ngram in n_grams]
    clean_n_grams = [ngram for ngram in clean_n_grams if ngram] # remove empty n-grams
    flat_n_grams = [word for ngram in n_grams for word in ngram]
    flat_clean_n_grams = [word for ngram in clean_n_grams for word in ngram]
    print "Set of unclean words: "
    print set(flat_n_grams).difference(set(flat_clean_n_grams))
    return clean_n_grams

def clean_all_tokens(tokens):
    clean_tokens = [filter(lambda word: is_clean_word(word),sentence) for sentence in tokens]
    clean_tokens = [sent for sent in clean_tokens if sent] # remove empty sentences
    return clean_tokens

from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder

def bi_collocations(tokens, num=20):
    from nltk.corpus import stopwords
    ignored_words = stopwords.words('english')

    word_list = [word for sent in tokens for word in sent]
    finder = BigramCollocationFinder.from_words(word_list,2)
    finder.apply_freq_filter(3)

    finder.apply_ngram_filter(lambda w1, w2:
                                  len(w1) < 3 \
                                  or len(w2) < 3 \
                                  or (len(w1)+len(w2)) < 8 \
                                  or w1.lower() in ignored_words \
                                  or w2.lower() in ignored_words) #length=2 want to keep e.g. rf pulse
    bigram_measures = BigramAssocMeasures()
    collocations = finder.nbest(bigram_measures.likelihood_ratio, num)
    return collocations

def tri_collocations(tokens, num=20):
    from nltk.corpus import stopwords
    ignored_words = stopwords.words('english')

    word_list = [word for sent in tokens for word in sent]
    finder = TrigramCollocationFinder.from_words(word_list)
    finder.apply_freq_filter(3)
    finder.apply_ngram_filter(lambda w1, w2, w3: 
                                  len(w1) < 3 \
                                  or len(w3) < 3 \
                                  or (len(w1)+len(w2)+len(w3)) < 11 \
                                  or w1.lower() in ignored_words \
                                  or w3.lower() in ignored_words)
    trigram_measures = TrigramAssocMeasures()
    collocations = finder.nbest(trigram_measures.likelihood_ratio, num)
    return collocations

def getCounts(noun_phrases):
    print "\tremoving tags..."
    tagFree_noun_phrases = chunks_without_tags(noun_phrases)
    print "\tlemmatizing..."
    lemmatized = lemmatize(tagFree_noun_phrases,verbose=False)
    print "\tcounting..."
    counts = Counter(tuple(l) for l in lemmatized)
    return counts

def applyCvalue(clean_noun_phrases,returnType,method='cvalue'):
    print "applying C-value method:"
    print "\tgrabbing nested noun phrases..."
    extended_noun_phrases = append_nested_noun_phrases(clean_noun_phrases)
    counts = getCounts(extended_noun_phrases)
    ## C-value reordering
    print "\tcalculating c-values and sorting by c-value..."
    c_vals = calc_c_values(counts)
    if method == 'wiki':
        return counts, dict(c_vals)
    if returnType == 'list':
        return [c[0] for c in c_vals] # sorted terms (highest weight)
    else: # returnType == 'dictionary'
        return dict(c_vals) # not sorted!
    ###########
    
def applyTfidf(clean_noun_phrases,returnType):
    print "applying tf-idf method:"
    counts = getCounts(clean_noun_phrases)
    ## tf-idf reordering
    filtered_terms = [key for key in counts.iterkeys() \
                          if counts[key] > 1]

    print "\tcalculating inverse document frequencies..."
    term_idf_dict = get_term_idf_dict(filtered_terms)

    term_tf_idf_dict = {} 

    max_count = counts.most_common(1)[0][1]
    for term in filtered_terms:
        tf = counts[term]
        idf = term_idf_dict[term]
        term_tf_idf_dict[term] = tf*math.log(idf,2)

    sorted_by_tf_idf = sorted(term_tf_idf_dict, \
                                  key=term_tf_idf_dict.get, \
                                  reverse = True)
    if returnType == 'list':
        return sorted_by_tf_idf
    else: # returnType == 'dictionary'
        return term_tf_idf_dict # not sorted!

def extract_term_list(txtFile,verbose=False,method='tfidf',returnType='list'):
    
    assert method == 'tfidf' or method == 'cvalue' \
        or method == 'countsWithNestedNPs' or method == 'countsNoNestedNPs'\
        or method == 'both' or method == 'wiki'
    assert returnType == 'list' or returnType == 'dictionary'

    if method == 'both' or method == 'wiki':
        print "tokenizing..."
        tokens = tokenize(txtFile)
        print "tagging parts of speech with stanford tagger..."
        tagged_tokens = stanford_tag(tokens)


    # # simple term extraction
    # all_n_grams = get_all_n_grams(tokens,2,4)
    # clean_n_grams = clean_all_n_grams(all_n_grams)
    # lemmatized = lemmatize(clean_n_grams)

    # # collocations
    # clean_tokens = clean_all_tokens(tokens)
    # lemmatized_tokens = lemmatize(clean_tokens)
    # lemmatized = bi_collocations(lemmatized_tokens,1000) + tri_collocations(lemmatized_tokens,1000)

    # print "tagging parts of speech with default tagger..."
    # tagged_tokens = tag(tokens)
    # # print tagged_tokens


    # print "tagging parts of speech with stanford tagger..."
    # tagged_tokens = stanford_tag(tokens)
    # print tagged_tokens

    # import cPickle as pickle
    # # with open(txtFile[:-4] + 'stanford_wsj_tagged.pickle','wb') as f:
    # #     pickle.dump(tagged_tokens,f)

    if not (method == 'both' or method == 'wiki'):
        print "loading pre-tagged pickle file..."
        import cPickle as pickle
        with open(txtFile[:-4] + 'stanford_wsj_tagged.pickle','rb') as f:
            tagged_tokens = pickle.load(f)

    print "simplifying tags..."
    simple_tagged_tokens = simplify_tags(tagged_tokens)
    # # print simple_tagged_tokens

    print "chunking noun phrases..."
    noun_phrases = noun_phrase_chunks(simple_tagged_tokens)
    # # print noun_phrases

    print "cleaning noun phrases..."
    clean_noun_phrases = clean_noun_phrase_chunks(noun_phrases)

    if method == 'both':
        return applyCvalue(clean_noun_phrases,returnType),\
            applyTfidf(clean_noun_phrases,returnType)

    if method == 'wiki':
        return applyCvalue(clean_noun_phrases,returnType,method)

    if method == 'cvalue' or method == 'countsWithNestedNPs'\
            or method == 'both':
        print "grabbing nested noun phrases..."
        extended_noun_phrases = append_nested_noun_phrases(clean_noun_phrases)
    elif method == 'tfidf' or method == 'countsNoNestedNPs':
        # # use below line and remove above line when not including nested nps.
        extended_noun_phrases = clean_noun_phrases

    ## the following will fail if method is not 'cvalue','tfidf','countsWithNestedNPs','countsNoNestedNPs'
    print "removing tags..."
    tagFree_noun_phrases = chunks_without_tags(extended_noun_phrases)

    print "lemmatizing..."
    lemmatized = lemmatize(tagFree_noun_phrases,verbose=False)

    print "counting..."
    counts = Counter(tuple(l) for l in lemmatized)

    ## Return sorted by frequency alone
    if method == 'countsWithNestedNPs' or method == 'countsNoNestedNPs':
        if returnType == 'list':
            return [c[0] for c in counts.most_common()]
        else: #returnType == 'dictionary' 
            return counts

    print "\nMost frequent 10 extracted terms:"
    for term in [c[0] for c in counts.most_common(10)]:
        print ' '.join([word for word in term])
    print

    if method == 'cvalue':
        ## C-value reordering
        print "calculating c-values and sorting by c-value..."
        c_vals = calc_c_values(counts)
        print "\nTop 10 by pure counts:"
        for i in counts.most_common(10):
            print i[0]
        print "\nTop 10 after reordering by c-value:"
        for i in c_vals[:10]:
            print " & " + ' '.join([word for word in i[0]])
        if returnType == 'list':
            return [c[0] for c in c_vals] # sorted terms (highest weight)
        else: # returnType == 'dictionary'
            return dict(c_vals) # not sorted!
        ###########

    # ## frequency filtering and reordering
    # filtered_terms = [key for key in counts.iterkeys() if counts[key] > 0]
    # def get_score(term):
    #     return math.log(2*counts[term],2)*math.log(len(term),2)
    # sorted_filtered_terms = sorted(filtered_terms, key=get_score, reverse=True)

    # return sorted_filtered_terms

    if method == 'tfidf': 
        ## tf-idf reordering
        filtered_terms = [key for key in counts.iterkeys() \
                              if counts[key] > 1]

        print "\ncalculating idfs..."
        term_idf_dict = get_term_idf_dict(filtered_terms)

        ## For speeding up testing:
        # ## pickle term_idf_dict as it is slow to calculate
        # ## saves the dict including nested nps just in case
        # # import cPickle as pickle
        # # with open(txtFile[:-4] + 'term_idf_dict.pickle','wb') as f:
        # #     pickle.dump(term_idf_dict,f) 

        # print "loading pre-calculated term_idf_dict pickle file..."
        # import cPickle as pickle
        # with open(txtFile[:-4] + 'term_idf_dict.pickle','rb') as f:
        #     term_idf_dict = pickle.load(f)

        # print term_idf_dict
        term_tf_idf_dict = {} 

        max_count = counts.most_common(1)[0][1]
        for term in filtered_terms:
            tf = counts[term]
            idf = term_idf_dict[term]
            term_tf_idf_dict[term] = tf*math.log(idf,2)

        sorted_by_tf_idf = sorted(term_tf_idf_dict, \
                                      key=term_tf_idf_dict.get, \
                                      reverse = True)
        print "\nTop 10 tf-idf sorted terms:"
        for term in sorted_by_tf_idf[:10]:
            print ' '.join([word for word in term])
        print
        if returnType == 'list':
            return sorted_by_tf_idf
        else: # returnType == 'dictionary'
            return term_tf_idf_dict # not sorted!



    

    

########################## Don't delete - Acronym finding ########
# def find_np_from_acronym(ac,nps):
#     def initials_match(string, phrase):
#         if len(string) != len(phrase):
#             return False
#         for it in xrange(0,len(string)):
#             if string[it].lower() != phrase[it][0].lower():
#                 return False
#         return True

#     alnum = filter(str.isalnum,ac)
#     return [np for np in nps if initials_match(alnum,np)]

# acrs = set(np[0] for np in tagFree if len(np) == 1 and is_acronym(np[0]))
# for ac in acrs:
#     print ac
#     nps = find_np_from_acronym(ac,tagFree)
#     if nps:
#         print ac, nps
######################################################################















    


# #### CODE FOR PRINTING NON-ALPHA CHARS IN RAW TEXT
# # nonAlphaChars = []
# # for char in raw:
# #     if not char.isalpha():
# #         nonAlphaChars += char

# # nonAlphaChars = sorted(set(nonAlphaChars))


# #### CODE FOR COMPARING THE TAGS OF BROWN VS WSJ/PENN 
# # tagged_tags = []
# # for sent in tagged:
# #     for (word, tag) in sent:
# #         tagged_tags.append(tag)
# # tagged_tags = sorted(set(tagged_tags))
# # print tagged_tags
# # t3_tagged_tags = []
# # for sent in t3tagged:
# #     for (word, tag) in sent:
# #         t3_tagged_tags.append(tag)
# # t3_tagged_tags = sorted(set(t3_tagged_tags))
# # print t3_tagged_tags


# ####CODE FOR TESTING NOUN PHRASE TAGS IN CONLL2000 CORPUS
# # from nltk.corpus import conll2000
# # train = conll2000.chunked_sents('train.txt')[0:5000]
# # nps = []
# # for t in train:
# #     traverse(t,nps)
# # #print nps

# # from nltk.tag.simplify import simplify_wsj_tag
# # nps_list = []
# # for np in nps:
# #     nps_list.append([simplify_wsj_tag(tag) for word, tag in np.leaves()])
# #     if (len(np.leaves()) == 3
# #     and simplify_wsj_tag(np.leaves()[0][1]) == 'VN'
# #     and simplify_wsj_tag(np.leaves()[1][1]) == 'N'
# #     and simplify_wsj_tag(np.leaves()[2][1]) == 'N'):
# #     # and simplify_wsj_tag(np.leaves()[3][1]) == 'N'): 
# #           #       print 'leaves: ', np.leaves(), ' has type ', type(np.leaves())
# #          print np.leaves()[0][0], np.leaves()[1][0], np.leaves()[2][0]#, np.leaves()[3][0]
# # # #print nps_list

# # nps_tuples = [tuple(l) for l in nps_list]
# # from nltk.probability import FreqDist
# # fd = FreqDist(nps_tuples)
# # fd_items = fd.items()
# # for it in fd_items[:int(len(fd_items)*0.1)]:
# #    print it



# ## Old grammar from unsimplified tags
# # grammar = r"""
# #     NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}
# #         {<NNP>+}
# #         {<NN>+}
# #            """


# ## Old dictionary checks
# # from enchant.checker import SpellChecker
# # chkr = SpellChecker(myDict, text=cleanRaw)
# # error_list = [err.word for err in chkr]
# # error_counts = collections.Counter(error_list)
# # print error_counts
# # error_set = set((error,count) for error, count in error_counts.iteritems() if count > 1)
# # print error_set
# # # error_set_filtered = [word for word in error_set if not in_dictionary(word)]
# # for word, count in error_set:
# #     print word, myDict.suggest(word)
# # print "errors: ", len(error_set)

# ####################################
# ## DICTIONARY STUFF
# ####################################

# import enchant
# #myDict = enchant.request_pwl_dict("./dictionary/dict3.txt")

# def in_dictionary(word):
#     if myDict.check(word.lower()) \
#        or myDict.check(word.capitalize()) \
#        or word[-2:] == "'s" \
#        or len(word) <= 5:
#         return True
#     return False

# def dictionary_checks(filename):
#     raw = rawTxt(filename)
#     cleanRaw = clearUpLines(raw)

#     from enchant.tokenize import get_tokenizer
#     tknzr = get_tokenizer()
#     words, errors = [], []
#     for (word,pos) in tknzr(cleanRaw):
#         if myDict.check(word):
#             words.append(word)
#         else:
#             errors.append(word)

#     words = sorted(set(words))
#     errors = sorted(set(error for error in errors if not in_dictionary(error)))
    
#     from enchant.pypwl import PyPWL
#     words_dict = PyPWL()
#     for word in words:
#         words_dict.add_to_session(word)

#     for error in errors:
#         print "From same text: ", error, words_dict.suggest(error)
#         print "From dictionary: ", error, myDict.suggest(error)

# # dictionary_checks('coursenotes.txt')


# # Natural Language Toolkit: code_unusual

# def unusual_words(text):
#     text_vocab = set(w.lower() for w in itertools.chain.from_iterable(text) if w.isalpha())
#     english_vocab = set(w.lower() for w in nltk.corpus.words.words())
#     unusual = text_vocab.difference(english_vocab)
#     return sorted(unusual)



# ####################################
# ####################################
