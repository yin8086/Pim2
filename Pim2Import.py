# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 16:20:06 2013

@author: Stardrad Yin
"""

import struct, os, fnmatch

from PIL import Image

tileW = 16
tileH = 8
folder = u'.'

def walk(adr):
    root,dirs,files = os.walk(adr).next()
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

def searchPal(col, pal, palBase, colNum):
    
    baseAddr = palBase * 0x10    
    palBuf = [( ord(pal[i]), ord(pal[i+1]), ord(pal[i+2]), ord(pal[i+3]) ) \
                for i in xrange(4 * baseAddr, 4 * (baseAddr + colNum), 4)]
    
    pal[4 * baseAddr:4 * (baseAddr + colNum)]
    

def toTile(tiles, tarW, tarH,\
             posX, posY, xOffset, yOffset, \
             pixBuf, pal, \
             palBase = 0, shift = 0, mark = 0xf):
    
    tileInW = tarW / tileW
    
    for picY in xrange(posY, posY + yOffset):
        for picX in xrange(posX, posX + xOffset):
            
            getInd = searchPal(pixBuf[picY*tarW + picX], pal, palBase, mark + 1)
                        
            tileOut = picY / tileH * tileInW + picX / tileW
            tileIn  = picY % tileH * tileW + picX % tileW 
            
            getInd = getInd << shift

            tiles[tileOut][tileIn] = getInd


def toPim2(fPtr, im, startAddr, layer):
    
    fPtr.seek(startAddr + 0x24)    
    width  = struct.unpack('<H', fPtr.read(2))[0]
    height = struct.unpack('<H', fPtr.read(2))[0]
    
    assert width == im.size[0], 'Width Error'
    assert height == im.size[1], 'Height Error'
 
    tileInW = width / tileW
    tileInH = height / tileH
    
    fPtr.seek(startAddr + 0x18)
    picSize = struct.unpack('<I', fPtr.read(4))[0]
    headerSize = struct.unpack('<H', fPtr.read(2))[0]
    palNum = struct.unpack('<H', fPtr.read(2))[0]
    
    picAddr = startAddr + headerSize + 0x10
    palBaseAddr = picAddr + picSize
    
    # fPtr.seek(picAddr)
    # tileArray = [list(fPtr.read(tileW * tileH)) for i in xrange(tileInW * tileInH)]
    tileArray = [[0 for i in xrange(tileW * tileH)] for j in xrange(tileInW * tileInH)]
    
    fPtr.seek(palBaseAddr)
    palBuf = fPtr.read(4 * palNum)


for curName in walk(u'.'):
    #with open(curName, 'rb') as fPtr:
    fName = curName[curName.rindex('\\') + 1:]
    oriName = fName[:-15]
    pos = int(fName[-14: -6], 16)
    layer = int(fName[-5: -4])
    if not os.path.isfile(os.path.join(folder, oriName)):
        continue
    im = Image.open(curName)
    with open(os.path.join(folder, oriName)) as binPtr:
            toPim2(binPtr, im, pos, layer)
            
