#!/usr/bin/python

import re


# functions ported from rmgarbage https://github.com/zw/rmgarbage

# Rule L: if string is longer than 40 characters, it is garbage
def too_long(string):
    if len(string) > 40:
        return True
    
    return False

# Rule A: if a string's ratio of alphanumeric characters to total characters 
# is less than 50%, the string is garbage
def bad_alnum_ratio(string):
    pattern = re.compile('[\W_]+') # matches [^A-Za-z0-9] (^ = not, _ is required)
    alnum_thresholds = { 1: 0,     # single chars can be non-alphanumeric
                         2: 0,     # so can doublets
                         3: 0.32,  # at least one of three should be alnum
                         4: 0.24,  # at least one of four should be alnum
                         5: 0.39 } # at least two of five should be alnum
              
    threshold = alnum_thresholds[len(string)] \
                if len(string) in alnum_thresholds else 0.5

    if len(string) == 0: # avoid division by zero
        return True 
    if float(len(pattern.sub('', string)))/len(string) < threshold:
        return True
    
    return False
    
# Rule R: if a string has 4 identical characters in a row, it is garbage
def has_4_consecutive(string):
    pattern = re.compile(r'((.)\2{3,})') # matches any 4 consecutive characters
    if pattern.search(string):
        return True
    
    return False

# Rule V: if a string has nothing but alphabetic characters, look at the
# number of consonants and vowels. If the number of one is less than 10% of
# the number of the other, then the string is garbage.
# This includes a length threshold.
def bad_cons_vowel_ratio(string):
    alpha_string = filter(str.isalpha, string)
    vowel_count = sum(1 for char in alpha_string if char in 'aeiouAEIOU')
    consonant_count = len(alpha_string) - vowel_count
    
    if (consonant_count > 0 and vowel_count > 0):
        ratio = float(vowel_count)/consonant_count
        if (ratio < 0.1 or ratio > 10):
            return True
    elif (vowel_count == 0 and consonant_count > len('rhythms')):
        return True
    elif (consonant_count == 0 and vowel_count > len('IEEE')):
        return True
    
    return False


# Rule P: "Strip off the first and last characters of a string. If there
# are two distinct punctuation characters in the result, then the string is
# garbage"
#
# Customisation: stripping off the last TWO characters as false positives
# included those ending with ').' and similar.
def has_two_distinct_puncts_inside(string):
    non_alnum_string = ''.join(char for char in string[1:-2] \
                               if not char.isalnum())
    for char in non_alnum_string[1:]:
        if char != non_alnum_string[0]:
            return True
    return False


# Rule C: "If a string begins and ends with a lowercase letter, then if
# the string contains an uppercase letter anywhere in between, then it is
# removed as garbage."
#
# Customisation: false positive on "needed.The". Exclude fullstop-capital.
# Extra customisation: Exclude hyphen-capital, apostrophe-capital and 
# forwardslash-capital
def has_uppercase_within_lowercase(string):
    if (string and string[0].islower() and string[-1].islower()):
        string_middle = string[1:-1]
        for index, char in enumerate(string_middle):
            if char.isupper() and not \
               (index > 0 and string_middle[index-1] in ".-'"):
                return True
    return False

def is_garbage(string):
    if too_long(string):
        return 'L'
    elif bad_alnum_ratio(string):
        return 'A'
    elif has_4_consecutive(string):
        return 'R'
    elif bad_cons_vowel_ratio(string):
        return 'V'
    elif has_two_distinct_puncts_inside(string):
        return 'P'
    elif has_uppercase_within_lowercase(string):
        return 'C'
    return False


    

if __name__ == '__main__':
    # test rmgarbage:
    import sys
    from nltk.corpus import PlaintextCorpusReader
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = raw_input("Directory root of corpus to be tested: ")
    corpus = PlaintextCorpusReader(root, '.*\.txt')

    for iD in corpus.fileids():
        print "Fileid: ", iD
        for string in corpus.raw(iD).split():
            returnValue = is_garbage(string)
            if returnValue:
                print returnValue, string
