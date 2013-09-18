# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 20:13:18 2013

@author: Stardrad
"""

import codecs,re
import os, fnmatch


workMode = 'utf16'


def convertCtr(match):
    return unichr(int(match.group()[1:5], 16))

invCtrlChars = re.compile(ur'\[[0-9a-f]{4}\]') 


def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            if fnmatch.fnmatch(name, '*.txt'):
                yield os.path.join(root, name)

def dealStr(mystr):
    return mystr
    

def getword(myf):
    for line in myf:
        wcv=line.strip(u'\r\n').split(u'=',1)
        yield wcv[1],int(wcv[0],16)

def getdata(myf):
    isfirst=True
    ltxt=[]
    add = 0
    length = -1
    for line in myf:
        if line.startswith(u'####'):
            if not isfirst:
                #print ltxt
                tmpStr = u''.join(ltxt)
                #print repr(tmpStr[:-4])
                yield add, length, tmpStr[:-4]
            else:isfirst=False
            ltxt=[]
            add=int(line[5:13],16)   
            if line[13] == u',':
                length = int(line[14:-7])
            else:
                length = -1
                
        else:
            ltxt.append(line)

    tmpStr = u''.join(ltxt)
    #print repr(tmpStr[:-4])
    yield add, length, tmpStr[:-4]  

with open('fix.log', 'wb') as f1:
    pass
isFirst = True
for curName in walk('.'):
    fName = curName[curName.rindex('\\') + 1:]
    print 'Process %s' % fName,
    
    

    if not os.path.isfile(curName[:-4]):
        print 'Pass'
        continue
    fSrc = open(curName[:-4], 'rb+')
    
    with codecs.open(curName,'rb','utf16') as txtsrc:
        txtnum = 0
        longnum = 0
        errStr = []
        for indadd, stdLen, unistr in getdata(txtsrc):
            
            if stdLen == -1: #not WQSG
                pass
            else: # WQSG
            
                unistr = invCtrlChars.sub(convertCtr, unistr)
                
                if workMode == 'utf16':
                    #unistr = unistr.replace('\r\n', u'\\n')
                    unistr = unistr.replace('\r\n', u'\n')
                tarCode = unistr.encode(workMode)
                if workMode == 'utf16':
                    tarCode = tarCode[2:]
                strLen = len(tarCode)
                if strLen > stdLen:
                    str0 = '\r\n' + ('%d' % longnum).center(35, '-')
                    str1 = u'%s' % unistr
                    str2 = (u'超出%d字节' % (strLen - stdLen)).center(35,'-')
                    errStr.append(str0)
                    errStr.append(str1)
                    errStr.append(str2)
                    longnum += 1
                    continue
                
                fSrc.seek(indadd)                
                fSrc.write(tarCode)
                fSrc.write('\x00' *(stdLen - strLen))
                    
                txtnum+=1
        
        if longnum > 0:
            with codecs.open('fix.log','ab','utf16') as fWrong:
                if isFirst:
                    isFirst = False
                else:
                    fWrong.write('\r\n')
                fWrong.write(fName.center(40, '*') + '\r\n')
                fWrong.write('\r\n'.join(errStr)+'\r\n')
        print u'共导入%d条文本, %d条文本超长'% (txtnum, longnum)
        fSrc.close()

    
    