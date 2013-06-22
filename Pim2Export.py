# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 23:35:28 2013

@author: Stardrad
"""

import struct, os, fnmatch, time

from PIL import Image

tileW = 16
tileH = 8
folder = r".\output"
Cimporve = 1

class BlockInfo:
    def __init__(self):
        self.posX = 0
        self.posY = 0
        self.xOffset = 0
        self.yOffset = 0
        self.pal16Index = 0
        self.info = '\x00\x00'
        self.shift = 0
        self.mark = 0
        


def checkDirs(tarDir):
    if not os.path.isdir(tarDir):
        os.mkdir(tarDir)

def walk(adr):
    root,dirs,files = os.walk(adr).next()
    for name in files:
        if not fnmatch.fnmatch(name, '*.py') and not fnmatch.fnmatch(name, '*.png'):
            yield os.path.join(root, name)

    
def printB(rhs):
    for myC in rhs:
        print '%02x' % ord(myC),
        
def findAddr(fPtr, tarStr):
    content = fPtr.read()
    begAdd = 0
    while True:
        fIndex = content.find(tarStr, begAdd)
        if fIndex != -1:
            begAdd = fIndex + len(tarStr)
            yield fIndex
        else:
            break

if Cimporve == 1:
    from tilemod import fromTile
else:
                
    def fromTile(pixBuf, tarW, tarH,\
                 posX, posY, xOffset, yOffset, \
                 tiles, pal, \
                 palBase = 0, shift = 0, mark = 0xf):
        
        tileInW = tarW / tileW
        
        for picY in xrange(posY, posY + yOffset):
            for picX in xrange(posX, posX + xOffset):
                tileOut = picY / tileH * tileInW + picX / tileW
                tileIn  = picY % tileH * tileW + picX % tileW 
                
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
    tileArray = [list(fPtr.read(tileW * tileH)) for i in xrange(tileInW * tileInH)]
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)
    
    if palNum > 0x100:
        mapAddr = startAddr + 0x40
    
        fPtr.seek(mapAddr + 4)
        blockNum = struct.unpack('<I', fPtr.read(4))[0]
        blockInfo = []
        for i in xrange(blockNum):
            bInfo = BlockInfo()
            bInfo.posX = struct.unpack('<H', fPtr.read(2))[0]
            bInfo.posY = struct.unpack('<H', fPtr.read(2))[0]
            bInfo.xOffset = struct.unpack('<H', fPtr.read(2))[0]
            bInfo.yOffset = struct.unpack('<H', fPtr.read(2))[0]
            bInfo.pal16Index = struct.unpack('<H', fPtr.read(2))[0]
            bInfo.info = fPtr.read(2)
            bInfo.shift = ord(fPtr.read(1))
            bInfo.mark = ord(fPtr.read(1))
            blockInfo.append(bInfo)
  
        lev0 = 0
        lev1 = 0
    
        pixBuf = [(0, 0, 0, 0)] * (width * height)
    
        for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid].shift != 4):                        
            lev0 += 1
            
            fromTile(pixBuf, width, height,\
                     blockInfo[blkInd].posX, blockInfo[blkInd].posY,\
                     blockInfo[blkInd].xOffset, blockInfo[blkInd].yOffset,\
                     tileArray, palBuf,\
                     blockInfo[blkInd].pal16Index,\
                     blockInfo[blkInd].shift, blockInfo[blkInd].mark)

        if lev0 > 0:
            im = Image.new('RGBA', (width, height))
            im.putdata(tuple(pixBuf))
            im.save('%s.0.png' % (os.path.join(folder, fName)))    
            print 'Save %s.0.png' % fName
       
        pixBuf = [(0, 0, 0, 0)] * (width * height)
        
        for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid].shift == 4):            
            lev1 +=  1

            fromTile(pixBuf, width, height,\
                     blockInfo[blkInd].posX, blockInfo[blkInd].posY,\
                     blockInfo[blkInd].xOffset, blockInfo[blkInd].yOffset,\
                     tileArray, palBuf,\
                     blockInfo[blkInd].pal16Index,\
                     blockInfo[blkInd].shift, blockInfo[blkInd].mark)
        
        if lev1 > 0:
            im = Image.new('RGBA', (width, height))
            im.putdata(tuple(pixBuf))
            im.save('%s.1.png' % (os.path.join(folder, fName)))    
            print 'Save %s.1.png' % fName
        
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
        im.save('%s.0.png' % (os.path.join(folder, fName)))    
        print 'Save %s.0.png' % fName

        
ntime = time.time()        
checkDirs(folder)    
for curName in walk(u'.'):
    with open(curName, 'rb') as fPtr:
        ind = 0
        fName = curName[curName.rindex('\\') + 1:]
        for stAdd in findAddr(fPtr, 'PIM2'):
            ind += 1            
            parsePIM(fPtr, stAdd, '%s.%08x' % (fName,stAdd) )
        if ind == 0:
            print 'Pass %s: no PIM2 included' % fName

print 'Total time: %lf' % (time.time() - ntime)


        
    