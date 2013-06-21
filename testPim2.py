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
        
def fromTile(pixBuf, tarW, tarH,\
             posX, posY, width, height, \
             tiles, pal, \
             palBase = 0, shift = 0, mark = 0xf):
    
    tileInW = width / tileW
    
    for picY in xrange(posY, posY + height):
        for picX in xrange(posX, posX + width):
            srcY = picY  #+ 2
            srcX = picX  #+ 2
            tileOut = srcY / tileH * tileInW + srcX / tileW
            tileIn  = srcY % tileH * tileW + srcX % tileW 
            getInd = ord(tiles[tileOut][tileIn])
            
            baseAddr = palBase * 0x10
            getInd = ( getInd & (mark << shift) ) >> shift


            colBuf = pal[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
            pixBuf[picY*tarW + picX] = tuple([ord(colCh) for colCh in colBuf])

            
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
            shift = ord(fPtr.read(1))
            mark = ord(fPtr.read(1))
            blockInfo.append([posX, posY, offX, offY, pal16ind, info1, shift, mark])
  
        lev0 = 0
        lev1 = 0
    
        pixBuf = [(0, 0, 0, 0)] * (width * height)
    
        for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid][6] != 4):                        
            lev0 += 1
            
            fromTile(pixBuf, width, height,\
                     blockInfo[blkInd][0], blockInfo[blkInd][1],\
                     blockInfo[blkInd][2], blockInfo[blkInd][3],\
                     tileArray, palBuf,\
                     blockInfo[blkInd][4], blockInfo[blkInd][6], blockInfo[blkInd][7])
        if lev0 > 0:
            im = Image.new('RGBA', (width, height))
            im.putdata(tuple(pixBuf))
            im.save(os.path.join(folder, fName) + '.0.png')    
            print 'Save ' + fName + '.0.png'
       
        pixBuf = [(0, 0, 0, 0)] * (width * height)
        
        for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid][6] == 4):            
            lev1 +=  1

            fromTile(pixBuf, width, height,\
                     blockInfo[blkInd][0], blockInfo[blkInd][1],\
                     blockInfo[blkInd][2], blockInfo[blkInd][3],\
                     tileArray, palBuf,\
                     blockInfo[blkInd][4], blockInfo[blkInd][6], blockInfo[blkInd][7])
        
        if lev1 > 0:
            im = Image.new('RGBA', (width, height))
            im.putdata(tuple(pixBuf))
            im.save(os.path.join(folder, fName) + '.1.png') 
            print 'Save ' + fName + '.1.png'
        
        # for blkInd in xrange(blockNum):
            # print 'Start x = %d, y = %d, endx = %d, endy = %d' % \
                               # (blockInfo[blkInd][0], \
                                # blockInfo[blkInd][1], \
                                # blockInfo[blkInd][0] + blockInfo[blkInd][2], \
                                # blockInfo[blkInd][1] + blockInfo[blkInd][3]),
            # print 'palInd = %d, offset = %02x, andNum = %02x' % (blockInfo[blkInd][4], blockInfo[blkInd][6], blockInfo[blkInd][7])
            
    elif palNum == 0x100:
        
        pixBuf = [(0, 0, 0, 0)] * (width * height)
        
        fromTile(pixBuf, width, height,\
                 0, 0,\
                 width, height,\
                 tileArray, palBuf,\
                 0, 0, 0xff)
        
        im = Image.new('RGBA', (width, height))
        im.putdata(tuple(pixBuf))
        im.save(os.path.join(folder, fName) + '.0.png') 
        print 'Save ' + fName + '.0.png'

        
        
checkDirs(folder)    
for curName in walk(u'.'):
    with open(curName, 'rb') as fPtr:
        ind = 0
        fName = curName[curName.rindex('\\') + 1:]
        for stAdd in findAddr(fPtr, 'PIM2'):
            ind += 1            
            parsePIM(fPtr, stAdd, fName + '.%08x' % stAdd)
        if ind == 0:
            print 'Pass %s: no PIM2 included' % fName
        


        
    