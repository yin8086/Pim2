# -*- coding: cp936 -*-
import os,struct,codecs,fnmatch
def walk(adr):
    mylist=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            mylist.append(adrlist)
    return mylist

fl = walk(u'.')
for fn in fl:
    if fnmatch.fnmatch(fn,'*.py'):
        continue
    infile = open(fn,'rb+')
    
    if infile.read(4) == 'OFS3':
        
        infile.seek(0xc)
        filesize = infile.read(4)
        files = struct.unpack('I',infile.read(4))[0]
        fn += '_unpacked'
        inoffset = (((files*8 + 0x14)/0x10) + 1) * 0x10
        if (files*8 + 0x14)%0x10 == 0:
            inoffset -= 0x10
        if not os.path.exists(fn):
            continue
        print u'当前进行封包的文件是：%s\n'%fn
        for i in xrange(files):
            data = open(fn + '\\' + '%s.bin'%i,'rb').read()
            #print 'headoffset:',hex(infile.tell()),'offset:',hex(inoffset-0x10),'size:',hex(len(data))
            infile.write(struct.pack('I',(inoffset-0x10)))
            sizeheadoff = infile.tell()
            infile.write(struct.pack('I',len(data)))
            nowoff = infile.tell()
            infile.seek(inoffset)
            infile.write(data)
            #size = infile.tell() - inoffset
            inoffset = ((infile.tell()/0x10) + 1) * 0x10
            if infile.tell()%0x10 == 0:
                inoffset -= 0x10
            #print hex(inoffset),hex(infile.tell()),hex(len(data))
            infile.write('\x00'*(inoffset - infile.tell()))
            endoff = infile.tell()
            infile.seek(sizeheadoff)
            infile.write(struct.pack('I',len(data)))
            infile.seek(nowoff)
            
            print fn + '\\' + '%s.bin'%i
        newfilesize = endoff - 0x10
        infile.seek(0xc)
        infile.write(struct.pack('I',newfilesize))
    infile.close()
