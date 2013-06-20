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
    fPtr = open(r"E:\SAOPicOut\title.bin", 'rb')
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
        offset = ord(fPtr.read(1))
        andNum = ord(fPtr.read(1))
        blockInfo.append([posX, posY, offX, offY, pal16ind, info1, offset, andNum])
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)

     
    tarW = width
    tarH = height
    pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)

    for picY in xrange(tarH):
        for picX in xrange(tarW):
            srcY = picY # + 2
            srcX = picX # + 2
            tileOut = srcY / tileH * tileInW + srcX / tileW
            tileIn  = srcY % tileH * tileW + srcX % tileW 
            getInd = ord(tileArray[tileOut][tileIn])
            
            baseAddr = palNum - 256
            #if blockInfo[blkInd][5] == '\x04\x03':
            
            # getInd = (getInd & (blockInfo[blkInd][7] << blockInfo[blkInd][6])) >> blockInfo[blkInd][6]


            colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
            pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
                
        #from PIL import Image
        #im = Image.new('RGBA', (tarW, tarH))
        #im.putdata(tuple(pixBuf))
        #im.save(r'E:\PVRTC\test3\part' + str(blkInd) + '.png')

    
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    #im.save(r'E:/test/' + str(fileN) + '.png')
    im.save(r'E:/test/full6_3.png') 
    
    tarW = width
    tarH = height
    pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)

    for blkInd in xrange(blockNum-1, -1, -1) : 
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
                
                baseAddr = 0
                #if blockInfo[blkInd][5] == '\x04\x03':
                
                # getInd = (getInd & (blockInfo[blkInd][7] << blockInfo[blkInd][6])) >> blockInfo[blkInd][6]


                colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
                pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
                
        from PIL import Image
        im = Image.new('RGBA', (tarW, tarH))
        im.putdata(tuple(pixBuf))
        im.save(r'E:\test\test1\part' + str(blkInd) + '.png')

    flag = [False] * blockNum
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    #im.save(r'E:/test/' + str(fileN) + '.png')
    im.save(r'E:/test/full6_0.png')    

    tarW = width
    tarH = height
    pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)

    for blkInd in xrange(blockNum-1, -1, -1) : 
        if blockInfo[blkInd][6] == 4:
            continue
        #tarW = width
        #tarH = height
        #pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
        for picY in xrange(blockInfo[blkInd][1], blockInfo[blkInd][1] + blockInfo[blkInd][3]):
            for picX in xrange(blockInfo[blkInd][0], blockInfo[blkInd][2] + blockInfo[blkInd][2]):
                srcY = picY  + 2
                srcX = picX  + 2
                tileOut = srcY / tileH * tileInW + srcX / tileW
                tileIn  = srcY % tileH * tileW + srcX % tileW 
                getInd = ord(tileArray[tileOut][tileIn])
                
                baseAddr = blockInfo[blkInd][4] * 0x10

                #if getInd & 0xf0 != 0 and not flag[blkInd] and blockInfo[blkInd][7] == 0xf:
                    #print 'X = %d, Y = %d, value = %d' % (picX, picY, getInd)
                    #flag[blkInd] = True
                getInd = getInd & blockInfo[blkInd][7]
                # getInd = (getInd & (blockInfo[blkInd][7] << blockInfo[blkInd][6])) >> blockInfo[blkInd][6]


                colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
                pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
                
        #from PIL import Image
        #im = Image.new('RGBA', (tarW, tarH))
        #im.putdata(tuple(pixBuf))
        #im.save(r'E:\test\test1\part' + str(blkInd) + '.png')


    for i,flg in enumerate(flag):
        if flg:
            print 'block %d error' % i
    
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    #im.save(r'E:/test/' + str(fileN) + '.png')
    im.save(r'E:/test/full6_1.png')    
   
    tarW = width
    tarH = height
    pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
    
    flag = [False] * blockNum
    
    for blkInd in xrange(blockNum-1, -1, -1) :         
        if blockInfo[blkInd][6] != 4:
            continue
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
                
                #if getInd & 0xf != 0 and not flag[blkInd] and blockInfo[blkInd][7] == 0xf:
                    #print 'X = %d, Y = %d, value = %d' % (picX, picY, getInd)
                    #flag[blkInd] = True
                baseAddr = blockInfo[blkInd][4] * 0x10
                #if blockInfo[blkInd][5] == '\x04\x03':
                
                #getInd = (getInd & (blockInfo[blkInd][7] << blockInfo[blkInd][6])) >> blockInfo[blkInd][6]
                getInd = (getInd & 0xf0) >> 4

                colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
                pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))
                
        from PIL import Image
        im = Image.new('RGBA', (tarW, tarH))
        im.putdata(tuple(pixBuf))
        im.save(r'E:\test\test2\part' + str(blkInd) + '.png')

    
    from PIL import Image
    im = Image.new('RGBA', (tarW, tarH))
    im.putdata(tuple(pixBuf))
    #im.save(r'E:/test/' + str(fileN) + '.png')
    im.save(r'E:/test/full6_2.png')
    
    print '================'
    for i,flg in enumerate(flag):
        if flg:
            print 'block %d error' % i
    for blkInd in xrange(blockNum):
        #print 'Start x = %d, y = %d, endx = %d, endy = %d' % \
        #                    (blockInfo[blkInd][0], \
        #                     blockInfo[blkInd][1], \
        #                     blockInfo[blkInd][0] + blockInfo[blkInd][2], \
        #                     blockInfo[blkInd][1] + blockInfo[blkInd][3]),
        print 'palInd = %d, offset = %02x, andNum = %02x' % (blockInfo[blkInd][4], blockInfo[blkInd][6], blockInfo[blkInd][7])
        
#    

        
    