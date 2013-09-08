#!/usr/bin/python
import wikiapi
import eventlet
from eventlet.green import urllib2
from collections import Counter
from xml.dom import minidom
import math
from tidyAndTokenizeTools import tidyAndTokenize
from nltk.util import ingrams
from nltk import ngrams
import numpy as np

def get_wiki_titles(term_list,verbose=False):
    wiki = wikiapi.WikiApi()
    
    def fetch_search_results(term_tuple):
        # takes a term tuple and gets the search results from wikipedia
        # returns a tuple of the term_tuple and the search results list
        search_term = ' '.join(term_tuple)
        url = wiki.get_better_search_url(search_term,6)
        content = urllib2.urlopen(url).read()
        search_results = wiki.get_better_search_results(content)
        return term_tuple, search_results
    
    pool = eventlet.GreenPool(250) # some fail if more than 250
    terms_with_results = []
    term_results_dict = {}
    for term, results in pool.imap(fetch_search_results,term_list):
        if verbose and not results:
            print "Term returned no results: ", term
            print
        else:
            terms_with_results.append(term)
            num_results = len(results)
            term_results_dict[term] = results
                    



    search_count = len(term_list)
    terms_with_results_count = len(terms_with_results)
    if verbose: print "Searches: ", search_count
    if verbose: print "Results:  ", terms_with_results_count
    percentage_with_results = 100*float(terms_with_results_count)/search_count
    if verbose: print "Percentage with results: ", percentage_with_results
    assert percentage_with_results > 90
    
    return term_results_dict

def get_hand_picked_titles(filename_part):
    hand_picked_titles = []
    with open('/homes/rps10/rps10Docs/Individual_Project/TermExtraction/hand-tagged-tests/wikiArticles/' + filename_part + '_wikis.txt') as f:
        for line in f:
            if line.split():
                url = line.split()[0]
                url_title = url.split('/')[-1]
                unquoted_url_title = urllib2.unquote(url_title).decode('utf8')
                title = ' '.join(unquoted_url_title.split('_'))
                hand_picked_titles.append(title)
    return hand_picked_titles
   

def compare_wiki_results(filename_part,retrieved_wiki_titles):
    hand_picked_titles = []
    with open('/homes/rps10/rps10Docs/Individual_Project/TermExtraction/hand-tagged-tests/wikiArticles/' + filename_part + '_wikis.txt') as f:
        for line in f:
            print line
            if line.split():
                url = line.split()[0]
                print repr(url)
                url_title = url.split('/')[-1]
                print repr(url_title)
                unquoted_url_title = urllib2.unquote(url_title).decode('utf8')
                print repr(unquoted_url_title)
                title = ' '.join(unquoted_url_title.split('_'))
                print repr(title)
                hand_picked_titles.append(title)
    print hand_picked_titles
    print "Titles not retrieved: "
    print set(hand_picked_titles).difference(set(retrieved_wiki_titles))


def get_wiki_content(title):
    # title is in unicode (utf-8) format with spaces, without underscores and
    # url escape characters

    wiki = wikiapi.WikiApi()

    spaces_to_underscores = '_'.join(title.split())
    utf8_encoded_title = spaces_to_underscores.encode('utf8')
    url_title = urllib2.quote(utf8_encoded_title) # url escape

    article_url = wiki.get_article_url(url_title)
    # print repr(article_url)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    content = opener.open(article_url).read()
    art = wiki.get_article(content)
    # print "Got article: ", art.heading
    # print "Content: ", art.content
    # print
    return art.content


def tokenize_article_content(content):
    # title is in unicode (utf-8) format with spaces, without underscores and
    # url escape characters
    tokens = tidyAndTokenize.TidyTokenizedText(raw_text = content).get_tidy_corpus_tokens()
    return tokens

def frequency_of_term_in_article(term,tokens):
    # term is a tuple of strings
    # tokens is a list of sentences, where sentences are a list of words
    return sum(1 for sent in tokens for ngram in ingrams(sent,len(term)) if tuple(ngram) == term)
    
def vector_sort(wiki_titles, terms_counts_dict, verbose=False):
    # wiki_titles is a list of wiki titles
    # terms_counts_dict is a dictionary with term tuples keys and counts values
    wiki = wikiapi.WikiApi()
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
   
    def title_to_article_url(title):
        spaces_to_underscores = '_'.join(title.split())
        utf8_encoded_title = spaces_to_underscores.encode('utf8')
        url_title = urllib2.quote(utf8_encoded_title) # url escape
        article_url = wiki.get_article_url(url_title)
        return article_url
    
    
   
    
    def fetch_content(wiki_title):
        # takes a wiki title and gets the page content
        # returns a tuple of the wiki title and the cosine value

        content = opener.open(title_to_article_url(wiki_title)).read()
        return wiki_title, content

    term_array = np.array(terms_counts_dict.values())
    pool = eventlet.GreenPool(250) # some fail if more than 250
    titles_cosines_dict = {}
    i = 1
    leng = len(wiki_titles)
    for wiki_title, content in pool.imap(fetch_content,wiki_titles[:100]):
        if verbose: print wiki_title
        if len(content) < 10: 
            assert False
        if verbose: print "tokenizing..."
        tokens = tokenize_article_content(wiki.get_article(content).content)
        if verbose: print "counting ngrams for tokens..."
        tokens_counter = Counter(ngram for sent in tokens for i in xrange(1,6) for ngram in ngrams(sent,i))
        if verbose: print "calculating array..."
        wiki_array = np.array([tokens_counter[term]*math.log(len(term)+1,2)\
                                   for term in terms_counts_dict.iterkeys()]) #*len(term)*len(term) 
        full_wiki_array = np.array(tokens_counter.values())

        if verbose: print "calculating cosine..."
        cosine_value = np.dot(term_array,wiki_array)/ \
            (np.linalg.norm(term_array) * np.linalg.norm(full_wiki_array))
        titles_cosines_dict[wiki_title] = cosine_value
        if verbose: print cosine_value
        if verbose: print i, '/', leng
        i += 1

    if verbose: print titles_cosines_dict
    if verbose: print
    sorted_titles_cosines = sorted(titles_cosines_dict, key=titles_cosines_dict.get, reverse = True)
    if verbose: print sorted_titles_cosines

    return sorted_titles_cosines


