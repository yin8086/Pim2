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
                
def writeAdd(fOut, pos, val):
    oldPos = fOut.tell()
    fOut.seek(pos)
    fOut.write(struct.pack('<I', val))
    fOut.seek(oldPos)

def getdata(myf, lineDeli):
    isfirst=True
    ltxt=[]
    add = 0
    for line in myf:
        if line.startswith(u'####'):
            if not isfirst:
                #print ltxt
                tmpStr = u''.join(ltxt)
                #print repr(tmpStr[:-4])
                yield add, tmpStr[:-4].replace(u'\r\n',lineDeli)
            else:isfirst=False
            ltxt=[]
            add=int(line[5:13],16)   
        else:
            ltxt.append(line)

    tmpStr = u''.join(ltxt)
    #print repr(tmpStr[:-4])
    yield add, tmpStr[:-4].replace(u'\r\n',lineDeli)                

def convertCtr(match):
    return unichr(int(match.group()[1:3], 16))

invCtrlChars = re.compile(ur'\{[0-9a-f]{2}\}') 
    
for curName in walk('script'):
    fName = curName[curName.rindex('\\') + 1:]
    print 'Start %s: ' % fName,
    tarStrList = []
    with codecs.open(curName, 'rb', 'utf16') as fSrc:
        for addr, unistr in getdata(fSrc, u'\x0a'):
            tarStrList.append( [addr, invCtrlChars.sub(convertCtr, unistr).encode('utf8')] )
    
    if len(tarStrList) > 0 and os.path.isfile(curName[:-4]):
        with open(curName[:-4], 'rb') as fOut:
            
            fOut.seek(0x8)
            f2StartAddr = struct.unpack('<I', fOut.read(4))[0]
            fOut.seek(f2StartAddr)
            # Pass prefix zeros
            preZero = 0
            while fOut.read(1) == '\x00':
                preZero += 1
            
            fOut.seek(-1, 1)
            
            oldAddr = fOut.tell()
            fOut.seek(0)
            headStr = fOut.read(oldAddr)

        with open(curName[:-4]+'.bin', 'wb') as fOut:

            fOut.write(headStr)
            
            isFirst = True
            
            for addr,unistr in tarStrList:
                if isFirst:
                    fOut.write(unistr)
                    isFirst = False
                else:
                    fOut.write('\x00')
                    writeAdd(fOut, addr, fOut.tell() - f2StartAddr)
                    fOut.write(unistr)
            
            fOut.write('\x00')
            fLen = fOut.tell() - f2StartAddr
            numAlign = 4 - (fOut.tell() & 3)
            if numAlign < 4:
                fOut.write('\x00' * numAlign)
            assert(fOut.tell() % 4 == 0) 
            writeAdd(fOut, 0xc, fLen)
                
        print 'import %d scripts' % len(tarStrList)
    else:
        print 'Pass'
                    
                    
                