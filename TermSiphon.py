#!/usr/bin/python
import sys
sys.dont_write_bytecode = True
import subprocess
from termExtraction import extract_term_list

def passArgsCheck(args):
    argsSize = len(args)
    if argsSize < 2:
        return False
    fileExtension = sys.argv[1][-4:]
    if not (fileExtension == '.txt' or fileExtension == '.pdf'):
        return False
    if argsSize > 2:
        try:
            returnSize = int(sys.argv[2])
        except Exception:
            return False
    return True

def convertToTxt(path):
    print "\nconverting PDF file to text using pdftotext..."
    txtFilePath = '/tmp/termSiphonTempTxtFile.txt'
    try:
        subprocess.check_output(['pdftotext','-enc','ASCII7',path,txtFilePath])
    except Exception:
        print "Problem converting pdf to text. Is the path correct?"
        sys.exit()
    return txtFilePath

def getTextFile(path):
    fileExtension = path[-4:]
    if fileExtension == '.txt':
        txtFilePath = path
    else: # fileExtension == '.pdf'
        txtFilePath = convertToTxt(path)
    return txtFilePath

if __name__ == '__main__':
   
    if not passArgsCheck(sys.argv):
        print "Arguments should be a path to a .txt or .pdf file and\noptionally an integer number of terms to be returned. \nFor example:\n./TermSiphon path/to/file.pdf 30"
        sys.exit()
    
    if len(sys.argv) > 2:
        returnSize = int(sys.argv[2])
    else: 
        returnSize = 20

    path = sys.argv[1]
    txtFilePath = getTextFile(path)
 
    cvalueList, tfidfList = extract_term_list(txtFilePath,verbose=True,\
                                                  method='both')

 
    maxTermStringLength = max(len(' '.join(word for word in term)) for term in cvalueList[:returnSize]+tfidfList[:returnSize])
    print "\n\n"+'-'*(maxTermStringLength*2+1)
    print ' '*(max(maxTermStringLength-8,0))+"Extracted Terms"
    print '-'*(maxTermStringLength*2+1)
    print "C-value".ljust(maxTermStringLength), "| tf-idf".ljust(maxTermStringLength)
    print '-'*maxTermStringLength, "| "+'-'*(maxTermStringLength-2)
    cvLength = len(cvalueList)
    tvLength = len(tfidfList)
    for i in xrange(0,returnSize):
        if i < cvLength or i < tvLength:
            if i < cvLength:
                print ' '.join(word for word in cvalueList[i]).ljust(maxTermStringLength),
            else:
                print ' '*maxTermStringLength,
            if i < tvLength:
                print ("| "+' '.join(word for word in tfidfList[i])).ljust(maxTermStringLength)
            else:
                print "|"
    print '-'*(maxTermStringLength*2+1)
    print

