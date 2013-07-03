import struct,fnmatch,codecs,os


def fSize(fn):
    with open(fn, 'rb') as fr:       
        fr.seek(0,2)
        retL = fr.tell()
    return retL
    
def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            yield os.path.join(root, name)
for fn in walk('script'):
    if fnmatch.fnmatch(fn,'*.txt'):
        continue
    print fn
    fp = open(fn,'rb')
    fs = fSize(fn)
    fp.seek(0x8)
    string_offset = struct.unpack('I',fp.read(4))[0]
    fp.seek(string_offset)
    
    dest = codecs.open(fn+'.txt','wb','utf16')
    i = 0
    while 1:
        if fp.tell() >= fs:
            break
        string = ''
        while 1:
            char = fp.read(1)
            if char == '\x00':
                break
            else:
                if char == '\x0a':
                    string += '\x0d\x0a'
                elif ord(char) < 32:
                    string += '[%02x]'%ord(char)
                else:
                    string += char
        if string == '':
            continue
        strings = string.decode('utf8')
        dest.write('#### %d ####\r\n%s\r\n\r\n'%(i,strings))
        i += 1
    dest.close()
    fp.close()
