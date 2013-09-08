#!/usr/bin/python

import enchant

class Dictionary:
    def __init__(self):
        self._dict = enchant.Dict('en_US')
        
    def in_dictionary(self,string):
        return self._dict.check(string)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        strings = raw_input("Words to be checked: ").split()
    else:
        strings = sys.argv[1:]
    
    myDict = Dictionary()
    for word in strings:
        if myDict.in_dictionary(word):
            print "'{}'".format(word), "found in dictionary."
        else:
            print "'{}'".format(word), "not found in dictionary."

