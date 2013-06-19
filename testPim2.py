# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 23:35:28 2013

@author: Stardrad
"""

import struct,sys

tileW = 16
tileH = 8

def printB(rhs):
    for myC in rhs:
        print '%02x' % ord(myC)
        
def readTiles(fPtr, tw, th):
    retTile = []
    for i in xrange(tw*th):
        retTile.append(list(fPtr.read(tileW * tileH)))
    return retTile
        
with open(sys.argv[1], 'rb') as fPtr:
    startAddr = 0xe40
        
    fPtr.seek(startAddr + 0x24)    
    width  = struct.unpack('<H', fPtr.read(2))[0]
    height = struct.unpack('<H', fPtr.read(2))[0]
    
    fPtr.seek(startAddr + 0x18)
    picSize = struct.unpack('<I', fPtr.read(4))[0]
    headerSize = struct.unpack('<H', fPtr.read(2))[0]
    palSize = struct.unpack('<H', fPtr.read(2))[0]
    
    mapAddr = startAddr + 0x40
    picAddr = startAddr + headerSize + 0x10
    palBaseAddr = picAddr + picSize
        
    tileInW = width / tileW
    tileInH = height / tileH
    
    fPtr.seek(picAddr)
    tileArray = readTiles(fPtr, tileInW, tileInH)

    fPtr.seek(mapAddr + 4)
    blockNum = struct.unpack('<I', fPtr.read(4))[0]
    
    posX = struct.unpack('<H', fPtr.read(2))[0]
    posY = struct.unpack('<H', fPtr.read(2))[0]
    offX = struct.unpack('<H', fPtr.read(2))[0]
    offY = struct.unpack('<H', fPtr.read(2))[0]
    
    fPtr.read(2)
    palStartInd = struct.unpack('<H', fPtr.read(2))[0]
    fPtr.read(2)
    
    fPtr.seek(palBaseAddr + palStartInd * 4)
    palBuf = fPtr.read(4*256)
    
    tarW = 480
    tarH = 272
    pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
    
    for picY in xrange(276, 276 + 80):
        for picX in xrange(0, 250):
            srcY = picY + 2
            srcX = picX + 2
            tileOut = srcY / tileH * tileInW + srcX / tileW
            tileIn  = srcY % tileH * tileW + srcX % tileW 
            getInd = ord(tileArray[tileOut][tileIn])
            colBuf = palBuf[4 * getInd:4 * getInd + 4]
            pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
    
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    im.save(r'E:/PVRTC/test.png')
#    for i in xrange(blockNum):
#        posX = struct.unpack('<H', fPtr.read(2))[0]
#        posY = struct.unpack('<H', fPtr.read(2))[0]
#        offX = struct.unpack('<H', fPtr.read(2))[0]
#        offY = struct.unpack('<H', fPtr.read(2))[0]
#        #sum += offX * offY
#        print 'Start: x=%3d, y=%3d, End: x=%3d, y=%3d' % (posX, posY, offX + posX, offY + posY), '|',
#        printB(fPtr.read(4))
#        printB(fPtr.read(2))
#        print
        
    