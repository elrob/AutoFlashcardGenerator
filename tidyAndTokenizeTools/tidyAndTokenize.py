#!/usr/bin/python

import garbageTidy
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from word_check import is_acronym, is_hyphenated, has_apostrophe, is_clean_word

class TidyTokenizedText:
    # Class attributes:
    ENG_STOPWORDS = set(stopwords.words('english'))
    WNL = WordNetLemmatizer()

    def __init__(self, filepath = None, raw_text = None):
        self._filepath = filepath
        self._raw_text = raw_text
    
    def contains_n_consecutive_alpha(self, n, s):
        # Returns true if string s contains n consecutive alphabet characters 
        regExp = re.compile(r'[a-zA-Z]{' + str(n) + r',}')
        if regExp.search(s):
            return True
        else:
            return False
    
    def is_useful_sentence(self,string):
        # a useful sentence has at least 6 consecutive alpha characters
        # or contains a hyphenated word, an acronym or a word like "l'Hopital"
        # or contains two consecutive words with at least 3 characters
        if self.contains_n_consecutive_alpha(6,string):
            return True
        words = string.split()
        prev_word_flag = False
        for word in words:
            if has_apostrophe(word) or is_hyphenated(word) or is_acronym(word):
                return True
            this_word_flag = self.contains_n_consecutive_alpha(3,word)
            if this_word_flag and prev_word_flag:
                return True
            prev_word_flag = this_word_flag
        return False

    def split_lines(self,list_of_strings):
        # splits each string in list_of_strings at line breaks unless
        # the following line starts with a lower-case letter.
        # returns a new list of all the strings including those which
        # have been split.
        new_list = []
        for string in list_of_strings:
            linesList = filter(None,string.splitlines(True))
            if linesList: # fixed bug where linesList could be empty
                new_list.append(linesList[0])
            for index in xrange(1,len(linesList)):
                if linesList[index].split(): # '\n' and '\x0c' lines are removed
                    if linesList[index].split()[0][0].islower():
                        new_list[-1] = new_list[-1] + linesList[index]
                    else:
                        new_list.append(linesList[index])
        return new_list
        
    
    # def split_on(self,list_of_strings,separator):
    #     new_list = []
    #     for string in list_of_strings:
    #         splitString = string.split(separator)
    #         for index in xrange(0,len(splitString)-1):
    #             splitString[index] = splitString[index] + separator
    #         new_list.extend(st for st in splitString if len(st.split()))
    #     return new_list

    def get_tidy_input_tokens(self):
        # "Load file, strip garbage strings, tokenize"

        if self._raw_text is None:
            self._raw_text = open(self._filepath).read()

        tidy_txt = garbageTidy.stripGarbage(self._raw_text,verbose = False)
        sentences = sent_tokenize(tidy_txt)
        
        split_sentences = self.split_lines(sentences)
  
        filtered_sents = [string for string in split_sentences \
                              if self.is_useful_sentence(string)]
        return [word_tokenize(sent) for sent in filtered_sents]

    # def get_tidy_input_tokens(self):
    #     "Load file, strip garbage strings, tokenize"
    #     raw_txt = open(self._filepath).read()
    #     tidy_txt = garbageTidy.stripGarbage(raw_txt)
    #     return [word_tokenize(sent) for sent in sent_tokenize(tidy_txt)]


    def get_tidy_corpus_tokens(self):
        "Call get_tidy_tokens and then: remove single characters, \
        remove stopwords, convert to lowercase, and lemmatize. \
        Finally remove any sentence that has no words."
        return [sent for sent in \
                [[self.WNL.lemmatize(word.lower()) \
                  for word in sent \
                  if is_clean_word(word)] \
                 for sent in self.get_tidy_input_tokens()] \
                if sent]
        # return [sent for sent in \
        #         [[self.WNL.lemmatize(word.lower()) \
        #           for word in sent \
        #           if len(word) > 1 and \
        #           not word.lower() in self.ENG_STOPWORDS] \
        #          for sent in self.get_tidy_input_tokens()] \
        #         if sent]

if __name__ == '__main__':
    # test rmgarbage:
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = raw_input("Enter file path to be tested: ")
    
    import time
    t0 = time.time()
    for sentence in TidyTokenizedText(filepath).get_tidy_corpus_tokens():
        print sentence
    t1 = time.time()
    print "Time taken: ", t1-t0
