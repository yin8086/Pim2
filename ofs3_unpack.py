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

    infile = open(fn,'rb')
    if infile.read(4) == 'OFS3':
        infile.seek(0xc)
        filesize = struct.unpack('I',infile.read(4))[0]
        files = struct.unpack('I',infile.read(4))[0]
        fn += '_unpacked'
        for i in xrange(files):
            offset = struct.unpack('I',infile.read(4))[0] + 0x10
            size = struct.unpack('I',infile.read(4))[0]
            nowoff = infile.tell()
            if (os.path.exists(fn)) != 1:
                os.mkdir(fn)
            upfile = open(fn + '\\' + '%s.bin'%i,'wb')
            infile.seek(offset)
            upfile.write(infile.read(size))
            upfile.close()
            infile.seek(nowoff)
            print fn + '\\' + '%s.bin'%i
        
    infile.close()
