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
        print '%02x' % ord(myC),
        
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
    palNum = struct.unpack('<H', fPtr.read(2))[0]
    
    mapAddr = startAddr + 0x40
    picAddr = startAddr + headerSize + 0x10
    palBaseAddr = picAddr + picSize
        
    tileInW = width / tileW
    tileInH = height / tileH
    
    fPtr.seek(picAddr)
    tileArray = readTiles(fPtr, tileInW, tileInH)

    fPtr.seek(mapAddr + 4)
    blockNum = struct.unpack('<I', fPtr.read(4))[0]
    blockInfo = []
    for i in xrange(blockNum):
        posX = struct.unpack('<H', fPtr.read(2))[0]
        posY = struct.unpack('<H', fPtr.read(2))[0]
        offX = struct.unpack('<H', fPtr.read(2))[0]
        offY = struct.unpack('<H', fPtr.read(2))[0]
        pal16ind = struct.unpack('<H', fPtr.read(2))[0]
        info1 = fPtr.read(2)
        info2 = fPtr.read(2)
        blockInfo.append([posX, posY, offX, offY, pal16ind, info1, info2])
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)

    
    #for fileN in xrange(20):

    
    #import random
    #for blkInd in random.sample(xrange(blockNum), 5) :
    flag = [False] * blockNum
    for blkInd in xrange(blockNum) :
        
        tarW = width
        tarH = height
        pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
        
        for picY in xrange(blockInfo[blkInd][1], blockInfo[blkInd][1] + blockInfo[blkInd][3]):
            for picX in xrange(blockInfo[blkInd][0], blockInfo[blkInd][2] + blockInfo[blkInd][2]):
                srcY = picY # + 2
                srcX = picX # + 2
                tileOut = srcY / tileH * tileInW + srcX / tileW
                tileIn  = srcY % tileH * tileW + srcX % tileW 
                getInd = ord(tileArray[tileOut][tileIn])
                
                baseAddr = blockInfo[blkInd][4] * 0x10
                if blockInfo[blkInd][5] == '\x04\x03' and getInd > 0xf:
                    if not flag[blkInd]:
                        flag[blkInd] = True
                    baseAddr = 0
                                    
                colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
                pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
                
        from PIL import Image
        im = Image.new('RGBA', (tarW, tarH))
        im.putdata(tuple(pixBuf))
        im.save(r'E:/test/part' + str(blkInd) + '.png')


    for i in xrange(blockNum):
        if flag[i]:
            print 'Block %d error' % i
    
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    #im.save(r'E:/test/' + str(fileN) + '.png')
    im.save(r'E:/test/full2.png')
    
    for blkInd in xrange(blockNum):
        printB(blockInfo[blkInd][4])
        print '|',
        printB(blockInfo[blkInd][5])
        print
        
#    

        
    