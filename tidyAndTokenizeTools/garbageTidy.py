#!/usr/bin/python

# Uses rmgarbage and dictionary check to remove garbage strings
# and small strings that don't appear in the dictionary.

import rmgarbage, dictionaryCheck
from unidecode import unidecode

myDict = dictionaryCheck.Dictionary()


# returns False if string is:
# a single character, a number, 
# a combination of upto 3 non-uppercase letters and numbers
def passes_dictionary_check(string):
    alnum_string = filter(str.isalnum, string)
    if len(alnum_string) == 1 and alnum_string not in 'aAI':
        return False
    elif alnum_string and len(filter(str.isalpha,alnum_string)) < 4:
        if not alnum_string.isupper() and not \
                myDict.in_dictionary(alnum_string):
            return False
    return True


def asciify(string):
    if isinstance(string,unicode):
        try:
            string = str(string)
        except:
            string = unidecode(string)
    return string

def stripGarbage(rawInput, verbose = False):
    returnedInput = ''
    for line in rawInput.splitlines():
           
        strippedline = '\x0c' if line.startswith('\x0c') else ''
        strings = (asciify(string) for string in line.split()) # a generator
        strippedline += ' '.join(string for string in strings \
                                if not rmgarbage.is_garbage(string) and \
                                passes_dictionary_check(string))
        strippedline += '\n'
        returnedInput += strippedline
        if verbose and line.split() != strippedline.split():
            print "Stripped garbage: ", line, " became ", strippedline
    return returnedInput


############ splits at all whitespace and eliminates all line breaks which
############ might be useful for sentence tokenization
# def stripGarbage(rawInput,verbose = False):
#     if verbose:
#         for string in rawInput.split():
#             if rmgarbage.is_garbage(string):
#                 print "{0:18} ==> {1}".format("Garbage string:", string)
#             elif not passes_dictionary_check(string):
#                 print "{0:18} ==> {1}".format("Not in dictionary:", string)
#     return ' '.join(string for string in rawInput.split() if not rmgarbage.is_garbage(string) and passes_dictionary_check(string))
 
if __name__ == '__main__':
    # test rmgarbage:
    import sys
    # from nltk.corpus import PlaintextCorpusReader
    # if len(sys.argv) > 1:
    #     root = sys.argv[1]
    # else:
    #     root = raw_input("Directory root of corpus to be tested: ")
    # corpus = PlaintextCorpusReader(root, '.*')

    # for iD in corpus.fileids():
    #     print garbageCheck(corpus.raw(iD))
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = raw_input("Enter file path to be tested: ")
   
    filehandle = open(filepath)
    print stripGarbage(filehandle.read(),verbose=True)
        
