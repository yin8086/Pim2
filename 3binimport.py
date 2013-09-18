# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 14:58:36 2013

@author: Stardrad Yin
"""

import codecs,struct,os,fnmatch

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

def getdata(myf):
    isfirst=True
    ltxt=[]
    for line in myf:
        if line.startswith(u'####'):
            if not isfirst:
                #print ltxt
                tmpStr = u''.join(ltxt)
                #print repr(tmpStr[:-4])
                yield tmpStr[:-4]
            else:isfirst=False
            ltxt=[]
                
        else:
            ltxt.append(line)

    tmpStr = u''.join(ltxt)
    #print repr(tmpStr[:-4])
    yield tmpStr[:-4] 
    
for curName in walk('.'):
    fLen = 0x20f0
    fName = curName[curName.rindex('\\') + 1:]
    print 'Process %s' % fName,
    
    if not os.path.isfile(curName[:-4]):
        print 'Pass'
        continue
    
    with open(curName[:-4], 'rb') as fSrc:
        fSrc.seek(0x10)
        fSrc.seek(4, 1)
        
        firstOff = struct.unpack('I',fSrc.read(4))[0]+0x10
        fSrc.seek(4, 1)
        offPos = fSrc.tell()
        
        fSrc.seek(0)
        headStr = fSrc.read(firstOff)
    
    with open(curName[:-4], 'wb+') as fSrc:
        fSrc.write(headStr)
        
        isFirst = True
        offI = 0
        with codecs.open(curName, 'rb', 'utf16') as txtSrc:
            txtnum = 0
            for unistr in getdata(txtSrc):
                unistr = unistr.replace('\r\n', u'\n')
                tarCode = unistr.encode('utf16')[2:]
                if isFirst:
                    fSrc.seek(firstOff)
                    fSrc.write(tarCode)
                    fSrc.write('\x00\x00')
                    isFirst = False
                else:
                    writeAdd(fSrc, offPos, fSrc.tell()-0x10)
                    fSrc.write(tarCode)
                    fSrc.write('\x00\x00')
                    offPos += 8
                txtnum += 1
            fSrc.write('\x00' * (fLen - fSrc.tell()))
        print u'共导入%d条文本'% txtnum
                    
        
        
        