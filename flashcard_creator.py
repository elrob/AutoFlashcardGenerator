#!/usr/bin/python

import urllib2, wikiapi, re, copy, textwrap, sys
from xml.dom import minidom
from nltk.tokenize import sent_tokenize, word_tokenize

def untokenize(tokens):
    text = ' '.join([' '.join(sent) for sent in tokens])
    """
Untokenizing a text undoes the tokenizing operation, restoring
punctuation and spaces to the places that people expect them to be.

Ideally, `untokenize(tokenize(text))` should be identical to `text`,
except for line breaks.
"""
    step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .', '...')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
      "can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()

def subsequence(needle, haystack):
    """
    Naive subsequence indexer; None if not found

    >>> needle = 'seven years ago'.split()
    >>> haystack = 'four score and seven years ago our fathers'.split()
    >>> print subsequence(needle, haystack)
    3
    """
    for i in xrange(len(haystack) - len(needle) + 1):
        if needle == haystack[i:i + len(needle)]: return i

def get_wikitext(wikiTitle):
    url = 'http://en.wikipedia.org/w/api.php?action=parse&format=xml&page='\
        + urllib2.quote(wikiTitle) + '&prop=wikitext'
    xmldoc = minidom.parseString(urllib2.urlopen(url).read())
    wikitext = xmldoc.getElementsByTagName('wikitext')[0].firstChild.data
    return wikitext

def get_wiki_summary(wikiTitle):
    wiki = wikiapi.WikiApi()

    article_url = wiki.get_article_url(urllib2.quote(wikiTitle))
    
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    content = opener.open(article_url).read()
    art = wiki.get_article(content)
    return art.summary


def get_cloze(wiki_title,sentence_start_index=0,number_of_sentences=1):

    wikitext = get_wikitext(wiki_title)
    clozes = [word_tokenize(phrase) for phrase in re.findall(re.escape("'''")+"(.*?)"+re.escape("'''"),wikitext)]

    tokens = [word_tokenize(sent) for sent in sent_tokenize(get_wiki_summary(wiki_title))[sentence_start_index:sentence_start_index+number_of_sentences]]
    cue_tokens = copy.deepcopy(tokens)
    lower_case_tokens = [[word.lower() for word in sent] for sent in tokens]

    for sent_index in xrange(0,len(cue_tokens)):
        for phrase in clozes:
            search_phrase = [word.lower() for word in phrase]
            word_index = subsequence(search_phrase,lower_case_tokens[sent_index])
            while word_index != None: # True even if 0
                for i in xrange(0,len(phrase)):
                    lower_case_tokens[sent_index][word_index+i] = \
                        '_'*len(lower_case_tokens[sent_index][word_index+i])
                    cue_tokens[sent_index][word_index+i] = \
                        '_'*len(lower_case_tokens[sent_index][word_index+i])

                word_index = subsequence(search_phrase,lower_case_tokens[sent_index])

    cue_side_text = untokenize(cue_tokens)
    response_side_text = untokenize(tokens)

    card_width=35
    cue_side_lines = textwrap.wrap(cue_side_text,card_width-2)
    response_side_lines = textwrap.wrap(response_side_text,card_width-2)
    print
    print
    print " An example flashcard for: ", "'"+wiki_title+"'"
    print " ---------------------------"+'-'*len("'"+wiki_title+"'")
    print " "+"Cue side:".ljust(card_width)+" ",\
        " "+"Response side:".ljust(card_width)+" "
    print " "+"_"*card_width+" "," "+"_"*card_width+" "
    print "|"+" "*card_width+"|","|"+" "*card_width+"|"
    for i in xrange(0,len(cue_side_lines)):
        sys.stdout.write('| ')
        sys.stdout.write(cue_side_lines[i].ljust(card_width-2))
        sys.stdout.write(' | | ')
        sys.stdout.write(response_side_lines[i].ljust(card_width-2))
        sys.stdout.write(' |\n')
        sys.stdout.flush()
    print "|"+" "*card_width+"|","|"+" "*card_width+"|"
    print "|"+" "*card_width+"|","|"+" "*card_width+"|"
    print "|"+"_"*card_width+"|","|"+"_"*card_width+"|"
    print
