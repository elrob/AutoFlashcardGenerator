#!/usr/bin/python
import sys
sys.dont_write_bytecode = True
import math
from TermSiphon import passArgsCheck, getTextFile
from termExtraction import extract_term_list
import wikiExtraction

def get_sorted_article_titles(txtFilePath):
    print "\nTERM EXTRACTION:"
    terms_counts_dict, terms_weights_dict = \
        extract_term_list(txtFilePath,verbose=True,method='wiki',\
                              returnType='dictionary')
                          

    search_terms_list = sorted(terms_weights_dict, \
                                  key=terms_weights_dict.get, \
                                  reverse = True)


    print
    print "WIKIPEDIA ARTICLE RETRIEVAL:"
    print "searching for articles..."
    # dict of term, results(list)
    retrieved_wiki_titles_dict = \
        wikiExtraction.get_wiki_titles(search_terms_list)

    print "sorting articles by relevance weighting..."
    all_results = {}
    for term in search_terms_list:
        if term in retrieved_wiki_titles_dict:
            results = retrieved_wiki_titles_dict[term]
            num_results = len(results)
            for title in results:
                weight = math.log(num_results - results.index(title)+1)*(math.log(terms_counts_dict[term]+1))
                if title in all_results:
                    all_results[title] = all_results[title] + weight
                else:
                    all_results[title] = weight

    relevance_weighting_list = sorted(all_results, key = all_results.get, reverse = True)

    print "sorting articles by cosine similarity..."
    cosine_similarity_list = wikiExtraction.vector_sort(relevance_weighting_list,terms_weights_dict)
    
    return relevance_weighting_list, cosine_similarity_list


if __name__ == '__main__':
    if not passArgsCheck(sys.argv):
        print "Arguments should be a path to a .txt or .pdf file and\noptionally an integer number of Wikipedia article titles to be returned. \nFor example:\n./Wikitriever path/to/file.pdf 15"
        sys.exit()

    if len(sys.argv) > 2:
        returnSize = int(sys.argv[2])
    else: 
        returnSize = 10

    path = sys.argv[1]
    txtFilePath = getTextFile(path)

    relevance_weighting_list, cosine_similarity_list = \
        get_sorted_article_titles(txtFilePath)

    maxTermStringLength = max(len(title) for title in relevance_weighting_list[:returnSize]+cosine_similarity_list[:returnSize])
    print "\n\n"+'-'*(maxTermStringLength*2+1)
    print ' '*(max(maxTermStringLength-15,0))+"Extracted Wikipedia Articles"
    print '-'*(maxTermStringLength*2+1)
    maxTermStringLength = max([maxTermStringLength,len("Relevance Weighting"),\
                                   len("Cosine Similarity")])
    print "Relevance Weighting".ljust(maxTermStringLength), "| Cosine Similarity".ljust(maxTermStringLength)
    print '-'*maxTermStringLength, "| "+'-'*(maxTermStringLength-2)
    rwLength = len(relevance_weighting_list)
    csLength = len(cosine_similarity_list)
    for i in xrange(0,returnSize):
        if i < rwLength or i < csLength:
            if i < rwLength:
                print relevance_weighting_list[i].ljust(maxTermStringLength),
            else:
                print ' '*maxTermStringLength,
            if i < csLength:
                print "| "+ cosine_similarity_list[i].ljust(maxTermStringLength)
            else:
                print "|"
    print '-'*(maxTermStringLength*2+1)
    print
