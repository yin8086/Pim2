# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 16:20:06 2013

@author: Stardrad Yin
"""

import struct, os, fnmatch, time

from PIL import Image

tileW = 16
tileH = 8
folder = u'.'
CImprove = 1

def pureName(curName):
    return curName[curName.rindex('\\') + 1:]
    
def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            if fnmatch.fnmatch(name, '*.png'):
                yield os.path.join(root, name)
                
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

if CImprove == 1:
    from tilemod import toTile
else:
    def searchPal(col, pal, palBase, colNum):
        
        baseAddr = palBase * 0x10    
        palBuf = [( ord(pal[i]), ord(pal[i+1]), ord(pal[i+2]), ord(pal[i+3]) ) \
                    for i in xrange(4 * baseAddr, 4 * (baseAddr + colNum), 4)]
        
        if col in palBuf:
            return palBuf.index(col)
        else:
            distanceList = []
            fR, fG, fB, fA = col
            for palCol in palBuf:
                tR, tG, tB, tA = palCol
                rMean = (fR * fA + tR * tA) / 510
                rDiff = (fR * fA - tR * tA) / 255
                gDiff = (fG * fA - tG * tA) / 255
                bDiff = (fB * fA - tB * tA) / 255
                aDiff = fA - tA
                dist  = (510 + rMean) * (rDiff**2) + \
                        1020 * (gDiff ** 2) + \
                        (765 - rMean) * (bDiff**2) + \
                        1530 * (aDiff**2)
                distanceList.append(dist)
                if dist == 0:
                    break
            minDist = min(distanceList)
            return distanceList.index(minDist)
    
    def toTile(tiles, tarW, tarH,\
                 posX, posY, xOffset, yOffset, \
                 pixBuf, pal, \
                 palBase = 0, shift = 0, mark = 0xf, bpp = 0):
        
        tileInW = tarW / tileW

        if bpp == 1:
            assert shift == 0 and mark == 0xff, 'Error fromTile'
            mark = 0xf

        for picY in xrange(posY, posY + yOffset):
            for picX in xrange(posX, posX + xOffset):
                
                getInd = searchPal(pixBuf[picY*tarW + picX], pal, palBase, mark + 1)
              
                tileOut = picY / tileH * tileInW + picX / tileW
                tileIn  = picY % tileH * tileW + picX % tileW 
                
                if mark == 0xf:
                    if bpp == 1:
                        shift = (tileIn & 1) << 2                   
                    # H(igh) L(ow)  H0 + 0L(4) 0L + H0(0)
                    bitOrigin = ord(tiles[tileOut][tileIn >> bpp]) &  ( 0xf << ((shift + 4) % 8) )
                    bitSet    = getInd << shift
                    getInd = bitOrigin + bitSet
                tiles[tileOut][tileIn >> bpp] = chr(getInd)


def toPim2(fPtr, im, startAddr, layer):
    
    fPtr.seek(startAddr + 0x24)    
    width  = struct.unpack('<H', fPtr.read(2))[0]
    height = struct.unpack('<H', fPtr.read(2))[0]
    
    assert width == im.size[0], 'Width Error'
    assert height == im.size[1], 'Height Error'

    fPtr.seek(startAddr + 0x18)
    picSize = struct.unpack('<I', fPtr.read(4))[0]
    headerSize = struct.unpack('<H', fPtr.read(2))[0]
    palNum = struct.unpack('<H', fPtr.read(2))[0]
    
    picAddr = startAddr + headerSize + 0x10
    palBaseAddr = picAddr + picSize
    
    fPtr.seek(startAddr + 0x22)
    dataType = ord(fPtr.read(1))
    if  dataType != 0x83 and dataType != 0x03:
        print '%s Other Pim2' % fName
        return
    
    picBpp = 5 - ord(fPtr.read(1))
    assert 0 <= picBpp <= 1, 'Err Bpp'

    global tileW, tileH
    if picBpp == 0:
        tileW = 16
        tileH = 8
    else:
        tileW = 32
        tileH = 8

    tileInW = width / tileW
    tileInH = height / tileH
    
    fPtr.seek(picAddr)
    tileArray = [list(fPtr.read( (tileW * tileH)>>picBpp )) for i in xrange(tileInW * tileInH)]
    # tileArray = [['\x00' for i in xrange(tileW * tileH)] for j in xrange(tileInW * tileInH)]
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)

    mapAddr = startAddr + 0x40
    fPtr.seek(mapAddr)    
    
    if fPtr.read(4) == 'BUW\x00':   
        assert picBpp != 1, '4bpp layer pic'

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
            
        pixBuf = list(im.getdata())
        if layer == 0: 
            for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid].shift != 4):                                   
        
                toTile(tileArray, width, height,\
                     blockInfo[blkInd].posX, blockInfo[blkInd].posY,\
                     blockInfo[blkInd].xOffset, blockInfo[blkInd].yOffset,\
                     pixBuf, palBuf,\
                     blockInfo[blkInd].pal16Index,\
                     blockInfo[blkInd].shift, blockInfo[blkInd].mark)  

        else:
            for blkInd in (bid for bid in xrange(blockNum) if blockInfo[bid].shift == 4):
                        
                toTile(tileArray, width, height,\
                     blockInfo[blkInd].posX, blockInfo[blkInd].posY,\
                     blockInfo[blkInd].xOffset, blockInfo[blkInd].yOffset,\
                     pixBuf, palBuf,\
                     blockInfo[blkInd].pal16Index,\
                     blockInfo[blkInd].shift, blockInfo[blkInd].mark) 

            
    else:
        pixBuf = list(im.getdata())
        
        toTile(tileArray, width, height,\
             0, 0,\
             width, height,\
             pixBuf, palBuf,\
             0, 0, 0xff, picBpp)  
        
    fPtr.seek(picAddr)        
    for tile in tileArray:
        fPtr.write(''.join(tile))
    print 'Import to %s at %08x @ layer %d' % (pureName(fPtr.name), startAddr, layer)

if __name__ == '__main__':
    ntime = time.time()  
    for curName in walk(u'.'):
        #with open(curName, 'rb') as fPtr:
        fName = pureName(curName)
        oriName = fName[:-15]
        pos = int(fName[-14: -6], 16)
        layer = int(fName[-5: -4])
        if not os.path.isfile(os.path.join(folder, oriName)):
            continue
        im = Image.open(curName).convert('RGBA')
        with open(os.path.join(folder, oriName), 'r+b') as binPtr:
                toPim2(binPtr, im, pos, layer)
    
    print 'Total time: %lf' % (time.time() - ntime)
