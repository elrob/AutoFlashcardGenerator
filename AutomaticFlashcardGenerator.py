#!/usr/bin/python
import sys
sys.dont_write_bytecode = True
import math, flashcard_creator
from TermSiphon import passArgsCheck, getTextFile
from termExtraction import extract_term_list
from Wikitriever import get_sorted_article_titles


if __name__ == '__main__':
    if not passArgsCheck(sys.argv):
        print "Arguments should be a path to a .txt or .pdf file and\noptionally an integer number of flashcards to be returned. \nFor example:\n./AutomaticFlashcardGenerator path/to/file.pdf 5"
        sys.exit()

    if len(sys.argv) > 2:
        returnSize = int(sys.argv[2])
    else: 
        returnSize = 5

    path = sys.argv[1]
    txtFilePath = getTextFile(path)

    cosine_similarity_list = get_sorted_article_titles(txtFilePath)[1]

    print "\nGENERATING FLASHCARDS:\n"
    for title in cosine_similarity_list[:returnSize]:
        flashcard_creator.get_cloze(title)
    
