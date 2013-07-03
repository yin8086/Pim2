# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 23:35:09 2013

@author: Stardrad
"""

import codecs,struct,os,fnmatch,re

def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            if fnmatch.fnmatch(name, '*.txt'):
                yield os.path.join(root, name)
                
                
def getdata(myf, lineDeli):
    isfirst=True
    ltxt=[]
    for line in myf:
        if line.startswith(u'####'):
            if not isfirst:
                #print ltxt
                tmpStr = u''.join(ltxt)
                #print repr(tmpStr[:-4])
                yield tmpStr[:-4].replace(u'\r\n',lineDeli)
            else:isfirst=False
            ltxt=[]
        else:
            ltxt.append(line)

    tmpStr = u''.join(ltxt)
    #print repr(tmpStr[:-4])
    yield tmpStr[:-4].replace(u'\r\n',lineDeli)                

def convertCtr(tar):
    fdIdx = 0
    while 1:
        fdIdx = tar.find(u'[', fdIdx)
        if fdIdx != -1 :
            pat = re.compile(u'g.*\[[0-9a-f]*\]')
            if pat.search(tar[:fdIdx+4]):
                fdIdx += 4
            elif (fdIdx + 3) < len(tar):
                if tar[fdIdx+3] == u']':
                    try:
                        code = int(tar[fdIdx+1:fdIdx+3], 16)
                        tar = ''.join([tar[:fdIdx], chr(code), tar[fdIdx+4:]])
                        fdIdx += 1
                    except ValueError:
                        fdIdx += 4
                else:
                    fdIdx += 1
            else:
                break        
        else:
            break
    return tar
    
for curName in walk('script'):
    fName = curName[curName.rindex('\\') + 1:]
    print 'Start %s: ' % fName,
    tarStrList = []
    with codecs.open(curName, 'rb', 'utf16') as fSrc:
        for unistr in getdata(fSrc, u'\x0a'):
            tarStrList.append( convertCtr(unistr).encode('utf8') )
    
    if len(tarStrList) > 0 and os.path.isfile(curName[:-4]):
        with open(curName[:-4], 'rb') as fOut:
            
            fOut.seek(0x8)
            fOut.seek(struct.unpack('<I', fOut.read(4))[0])
            # Pass prefix zeros
            preZero = 0
            while fOut.read(1) == '\x00':
                preZero += 1
            
            fOut.seek(-1, 1)
            
            oldAddr = fOut.tell()
            fOut.seek(0)
            headStr = fOut.read(oldAddr)

        with open(curName[:-4]+'.bin', 'wb') as fOut:
            finalStr = '\x00'.join(tarStrList)
            fLen = len(finalStr) + preZero
            
            fOut.write(headStr)
            fOut.write(finalStr)
            numAlign = 4 - (fOut.tell() & 3)
            fOut.write('\x00' * numAlign)
            assert(fOut.tell() % 4 == 0)            
            fOut.seek(0xc)
            fOut.write(struct.pack('<I', fLen))
                
        print 'import %d scripts' % len(tarStrList)
    else:
        print 'Pass'
                    
                    
                