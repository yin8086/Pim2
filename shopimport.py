# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:30:28 2013

@author: Stardrad Yin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 14:58:36 2013

@author: Stardrad Yin
"""

import codecs,struct,os,fnmatch,sys

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
    
curName = 'shop.bin'
print 'Process shop.bin'


offsetA = 0x16b10
offsetB = 0x22e50
offsetC = 0x23740

with open(curName, 'rb+') as fSrc:
    
    # offsetA
    fSrc.seek(offsetA)
    fSrc.seek(4, 1) #num
    
    firstOff = struct.unpack('I',fSrc.read(4))[0]+ offsetA
    fSrc.seek(4, 1)
    offPos = fSrc.tell()
    
    isFirst = True
    with codecs.open(curName + ('_%5x.txt' % offsetA), 'rb', 'utf16') as txtSrc:
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
                writeAdd(fSrc, offPos, fSrc.tell()-offsetA)
                fSrc.write(tarCode)
                fSrc.write('\x00\x00')
                offPos += 8
            txtnum += 1
        if fSrc.tell() > offsetB:
            print 'Big A Error @ %08x' % fSrc.tell()
            sys.exit(0)
        else:
            fSrc.write('\x00' * (offsetB - fSrc.tell() - 0x10))
            
    print '%08x %d scripts imported' % (offsetA, txtnum)
    
    # offsetB
    fSrc.seek(offsetB)
    fSrc.seek(4, 1) #num
    
    firstOff = struct.unpack('I',fSrc.read(4))[0]+ offsetB
    fSrc.seek(4, 1)
    offPos = fSrc.tell()
    
    
    isFirst = True
    with codecs.open(curName + ('_%5x.txt' % offsetB), 'rb', 'utf16') as txtSrc:
        txtnum = 0
        for unistr in getdata(txtSrc):
            unistr = unistr.replace('\r\n', u'\n')
            tarCode = unistr.encode('utf8')
            
            if isFirst:
                fSrc.seek(firstOff)
                fSrc.write(tarCode)
                fSrc.write('\x00\x00')
                isFirst = False
            else:
                writeAdd(fSrc, offPos, fSrc.tell()-offsetB)
                fSrc.write(tarCode)
                fSrc.write('\x00\x00')
                offPos += 8
            txtnum += 1
        if fSrc.tell() > offsetC:
            print 'Big B Error @ %08x' % fSrc.tell()
            sys.exit(0)
        else:
            fSrc.write('\x00' * (offsetC - fSrc.tell()))
                
    print '%08x %d scripts imported' % (offsetB, txtnum)
    
    
                    
        
        
        