#!/usr/bin/python

import glob
import cPickle as pickle
import sqlite3 as lite


def termToString(term):
    return ':'.join(term)

from collections import defaultdict
docFreqDict = defaultdict(int)
for folder in glob.glob('./document_frequencies/*'):
    print len(docFreqDict)
    print folder
    for i in xrange(1,6):
        print i
        with open(folder + '/Doc_Freqs_Of' + str(i) + 'grams.pickle') as f:
            import cPickle as pickle
            d = pickle.load(f)
            d_dict = d.dictOfTermsAndDocFreqs
        for term in d_dict:
            if i == 1:
                newTerm = term,
                newTerm = unicode(termToString(newTerm))
                docFreqDict[newTerm] = docFreqDict[newTerm] + d_dict[term]
            else:
                newTerm = unicode(termToString(term))
                docFreqDict[newTerm] = docFreqDict[newTerm] + d_dict[term]
            # print '**'
        # print docFreqDict[term]

        # print docFreqDict[term]
        # print '**'

print "Max value", max(value for value in docFreqDict.itervalues())
# sortedUnicodeKeys = sorted(key for key in docFreqDict.iterkeys())

# print "SORTED"
# import datrie
# import string

# tenth = len(docFreqDict)/10
# for i in xrange(1,11):
#     trie = datrie.BaseTrie(string.printable)

#     l = tenth
#     count = 1

#     for key in sortedUnicodeKeys[i*tenth:(i+1)*tenth]:
#         if count % 1000 == 1:
#             print count
#             print l
#         trie[key] = docFreqDict[key]
#         count += 1

#     trie.save('my.trie'+str(i))
# # con = lite.connect('./sqliteTest/test.db')
# # with con:
# #     cur = con.cursor()
# #     cur.execute("DROP TABLE IF EXISTS Terms")
# #     cur.execute("CREATE TABLE Terms(Term TEXT, DocFreq INT)")
# #     cur.executemany("INSERT INTO Terms VALUES (?,?)", ((termToString(key),docFreqDict[key]) for key in docFreqDict.iterkeys()))

for x in docFreqDict.keys()[:1000]:
    print x
print len(docFreqDict)

y = zip(docFreqDict.iterkeys(),docFreqDict.itervalues())
print y[:100]
