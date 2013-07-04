import struct,fnmatch,codecs,os,re


def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            if not fnmatch.fnmatch(name, '*.txt'):
                yield os.path.join(root, name)
                
def readUntilZ(myf):
    restr=[]
    while True:
        byteg=myf.read(1)
        if byteg=='\x00':break
        restr.append(byteg)
    
    return ''.join(restr)

def convertCtr(match):
    return u'{{{0:02x}}}'.format(ord(match.group()))

def parseStr(tar):
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
                        tar = ''.join([tar[:fdIdx], '{' ,tar[fdIdx+1:fdIdx+3], '}' ,tar[fdIdx+4:]])
                        fdIdx += 4
                    except ValueError:
                        fdIdx += 4
                else:
                    fdIdx += 1
            else:
                break        
        else:
            break
    return tar

def printB(rhs):
    for mbyte in rhs:
        print '%02x' % ord(mbyte),

def getRealAdd(strOff, ptrBuf, start):
    fdIdx = ptrBuf.find('\x08\x00' + struct.pack('<I', strOff), start)    
    if fdIdx == -1:
        return 0
    else:
        return fdIdx + 2

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

ctrlChars = re.compile(ur'[\x00-\x09\x0b-\x0c\x0e-\x1f]') 
       
for curName in walk('script'):
    fName = curName[curName.rindex('\\') + 1:]
    print 'Start %s: ' % fName,
    outList = []
    chscrN = curName.replace('script\\', r'chscript\\')+'.txt'
    tarStrList = []
    
    if os.path.isfile(chscrN):
        with codecs.open(chscrN, 'rb', 'utf16') as fRef:
            for unistr in getdata(fRef):
                tarStrList.append( parseStr(unistr))

        with open(curName, 'rb') as fSrc:
            f1Start = struct.unpack('<I', fSrc.read(4))[0]
            f1Len = struct.unpack('<I', fSrc.read(4))[0]
            f2Start = struct.unpack('<I', fSrc.read(4))[0]
            f2Len = struct.unpack('<I', fSrc.read(4))[0]
            
            fSrc.seek(f1Start)
            ptrBuf = fSrc.read(f1Len)
            
            fSrc.seek(f2Start)
             
             
            while fSrc.read(1) == '\x00':
                pass
            if fSrc.tell() < f2Start + f2Len: # not EOF
                fSrc.seek(-1,1)
                searchAdd = 0
                idx = 0
                while fSrc.tell() < f2Start + f2Len:                   
                    curOff = fSrc.tell() - f2Start            
                    curStr = readUntilZ(fSrc)
                    curTOff = getRealAdd(curOff, ptrBuf, searchAdd)
                    assert curTOff != 0, 'Error'
                    # curStr2 = ctrlChars.sub(convertCtr, curStr.replace('\x0a','\r\n').decode('utf8'))
                    if curStr == '':
                        curStr = u''
                    else:
                        if tarStrList[idx] == u'':
                            curStr = ctrlChars.sub(convertCtr, curStr.replace('\x0a','\r\n').decode('utf8'))
                        else:
                            curStr = ctrlChars.sub(convertCtr, tarStrList[idx])
                        idx += 1
                    outList.append([curTOff+f1Start, curStr])
                    searchAdd = curTOff + 4
                    
    
        if len(outList) > 0:
            with codecs.open(curName + '.txt', 'wb', 'utf16') as fOut:
                for textAdd, textStr in outList:
                    fOut.write('#### %08x ####\r\n%s\r\n\r\n' % (textAdd, textStr))
                print 'export %d script' % len(outList)
    
        else:
            print 'Pass 1'
    else:
        print 'Pass 2'
            
        
