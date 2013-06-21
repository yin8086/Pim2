# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 23:35:28 2013

@author: Stardrad
"""

import struct, os, fnmatch

from PIL import Image

tileW = 16
tileH = 8
folder = r".\output"

def checkDirs(tarDir):
    if not os.path.isdir(tarDir):
        os.mkdir(tarDir)

def walk(adr):
    for root,dirs,files in os.walk(adr):
        for name in files:
            if not fnmatch.fnmatch(name, '*.py') and not fnmatch.fnmatch(name, '*.png'):
                adrlist=os.path.join(root, name)
                yield adrlist

    
def printB(rhs):
    for myC in rhs:
        print '%02x' % ord(myC),
        
def readTiles(fPtr, tw, th):
    retTile = []
    for i in xrange(tw*th):
        retTile.append(list(fPtr.read(tileW * tileH)))
    return retTile

def findAddr(fPtr, tarStr):
    while True:
        buf = fPtr.read(len(tarStr))
        if len(buf) < len(tarStr):
            break
        elif buf != tarStr:
            fPtr.seek(-len(buf) + 1, 1)
            continue
        else:
            yield fPtr.tell() - len(tarStr)
        
        
def parsePIM(fPtr, startAddr, fName):
    
    fPtr.seek(startAddr + 0x24)    
    width  = struct.unpack('<H', fPtr.read(2))[0]
    height = struct.unpack('<H', fPtr.read(2))[0]
    
    tileInW = width / tileW
    tileInH = height / tileH
    
    fPtr.seek(startAddr + 0x18)
    picSize = struct.unpack('<I', fPtr.read(4))[0]
    headerSize = struct.unpack('<H', fPtr.read(2))[0]
    palNum = struct.unpack('<H', fPtr.read(2))[0]
    
    picAddr = startAddr + headerSize + 0x10
    palBaseAddr = picAddr + picSize
    
    fPtr.seek(picAddr)
    tileArray = readTiles(fPtr, tileInW, tileInH)
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)
    
    if palNum > 0x100:
        mapAddr = startAddr + 0x40
    
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
        

        
        lev0 = 0
        lev1 = 0
    
        tarW = width
        tarH = height
        pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
    
        for blkInd in xrange(blockNum) : 
            if blockInfo[blkInd][6] == 4:
                continue
            lev0 += 1
            #tarW = width
            #tarH = height
            #pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
    
            for picY in xrange(blockInfo[blkInd][1], blockInfo[blkInd][1] + blockInfo[blkInd][3]):
                for picX in xrange(blockInfo[blkInd][0], blockInfo[blkInd][0] + blockInfo[blkInd][2]):
                    srcY = picY  #+ 2
                    srcX = picX  #+ 2
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
    
    
        # for i,flg in enumerate(flag):
            # if flg:
                # print 'block %d error' % i
        if lev0 > 0:
            im = Image.new('RGBA', (tarW, tarH))
            im.putdata(tuple(pixBuf))
            #im.save(r'E:/test/' + str(fileN) + '.png')
            im.save(folder + fName + '.0.png')    
            print 'Save ' + fName + '.0.png'
       
        tarW = width
        tarH = height
        pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
        
        #flag = [False] * blockNum
        
        for blkInd in xrange(blockNum) :         
            if blockInfo[blkInd][6] != 4:
                continue
            lev1 +=  1
            # tarW = width
            # tarH = height
            # pixBuf = [(0, 0, 0, 0)] * (tarW * tarH)
            for picY in xrange(blockInfo[blkInd][1], blockInfo[blkInd][1] + blockInfo[blkInd][3]):
                for picX in xrange(blockInfo[blkInd][0], blockInfo[blkInd][0] + blockInfo[blkInd][2]):
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
                    
            # from PIL import Image
            # im = Image.new('RGBA', (tarW, tarH))
            # im.putdata(tuple(pixBuf))
            # im.save(r'E:\test\test2\part' + str(blkInd) + '.png')
    
        
        if lev1 > 0:
            im = Image.new('RGBA', (tarW, tarH))
            im.putdata(tuple(pixBuf))
            #im.save(r'E:/test/' + str(fileN) + '.png')
            im.save(folder + fName + '.1.png') 
            print 'Save ' + fName + '.1.png'
        
        # print '================'
        # for i,flg in enumerate(flag):
            # if flg:
                # print 'block %d error' % i
        # for blkInd in xrange(blockNum):
            # print 'Start x = %d, y = %d, endx = %d, endy = %d' % \
                               # (blockInfo[blkInd][0], \
                                # blockInfo[blkInd][1], \
                                # blockInfo[blkInd][0] + blockInfo[blkInd][2], \
                                # blockInfo[blkInd][1] + blockInfo[blkInd][3]),
            # print 'palInd = %d, offset = %02x, andNum = %02x' % (blockInfo[blkInd][4], blockInfo[blkInd][6], blockInfo[blkInd][7])
            
    elif palNum == 0x100:
        
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
                
                baseAddr = 0
                colBuf = palBuf[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
                pixBuf[picY*tarW + picX] = (ord(colBuf[0]), ord(colBuf[1]), ord(colBuf[2]), ord(colBuf[3]))

        im = Image.new('RGBA', (tarW, tarH))
        im.putdata(tuple(pixBuf))
        #im.save(r'E:/test/' + str(fileN) + '.png')
        im.save(folder + fName + '.0.png') 
        print 'Save ' + fName + '.0.png'

        
        
checkDirs(folder)    
for curName in walk(u'.'):
    with open(curName, 'rb') as fPtr:
        ind = 0
        for stAdd in findAddr(fPtr, 'PIM2'):
            fName = curName[curName.rindex('\\'):]
            parsePIM(fPtr, stAdd, fName + '.%d' % ind)
            ind += 1
        
        
        
#    

        
    