import re
from nltk.corpus import stopwords
ENG_STOPWORDS = stopwords.words('english')

def is_acronym(s):
    # Returns true if string s has at least 3 consecutive 
    # upper case letters. Includes 'fMRI' and 'CD-ROM' but not
    # 'Laser', 'kWh'. It may be possible to improve this.
    alnum = filter(str.isalnum,s)
    regExp = re.compile(r'[A-Z]{3,}')
    if len(alnum) < 7 and regExp.search(alnum):
        return True
    else:
        return False

def is_hyphenated(word):
    # word is at least 5 chars including a hyphen inside
    return len(word) > 4 and '-' in word[1:-1]

def has_apostrophe(word):
    # word is at least 4 chars including an apostrophe not at the end
    # e.g. l'Hopital, d'Alembert
    return len(word) > 3 and "'" in word[1:-1]

def is_clean_word(word, verbose=False):
        
    if (len(word) < 2) or (word.lower() in ENG_STOPWORDS):
        if verbose: print word, " is not a clean word in is_clean_word."
        return False
    elif not (word.isalnum() or has_apostrophe(word) or \
                  is_hyphenated(word) or is_acronym(word)):
        if verbose: print word, " is not a clean word in is_clean_word."
        return False
    else:
        return True

    
