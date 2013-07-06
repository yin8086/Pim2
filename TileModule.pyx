def fromTile(pixBuf, int tarW, int tarH,\
             int posX, int posY, int xOffset, int yOffset, \
             tiles, pal, \
             int palBase, int shift, int mark, int bpp = 0):
    
    cdef int tileH = 8
    cdef int tileW = 16 << bpp
    
    cdef int tileInW = tarW / tileW
  
    cdef int tileOut
    cdef int tileIn
    cdef int getInd
    cdef int baseAddr
    
    cdef int picY
    cdef int picX
    
    if bpp == 1:
        # assert shift == 0 and mark == 0xff, 'Error fromTile'
        mark = 0xf
    
    for picY in xrange(posY, posY + yOffset):
        for picX in xrange(posX, posX + xOffset):
            tileOut = picY / tileH * tileInW + picX / tileW
            tileIn  = picY % tileH * tileW + picX % tileW 
            
            getInd = ord(tiles[tileOut][tileIn >> bpp])
            
            if bpp == 1:
                shift = (tileIn & 1) << 2
            
            baseAddr = palBase * 0x10
            getInd = ( getInd & (mark << shift) ) >> shift


            colBuf = pal[4 * (baseAddr + getInd): 4 * (baseAddr + getInd) + 4]
            pixBuf[picY*tarW + picX] = tuple([ord(colCh) for colCh in colBuf])
            
cdef int searchPal(col, pal, int palBase, int colNum):
    
    cdef int baseAddr = palBase * 0x10    
    palBuf = [( ord(pal[i]), ord(pal[i+1]), ord(pal[i+2]), ord(pal[i+3]) ) \
                for i in xrange(4 * baseAddr, 4 * (baseAddr + colNum), 4)]
    
    cdef double rMean
    cdef double rDiff, gDiff, bDiff, aDiff
    cdef double dist
    cdef int fR, fG, fB, fA
    cdef int tR, tG, tB, tA
    
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
        
def toTile(tiles, int tarW, int tarH,\
             int posX, int posY, int xOffset, int yOffset, \
             pixBuf, pal, \
             int palBase, int shift, int mark, int bpp = 0):
    
    cdef int tileH = 8
    cdef int tileW = 16 << bpp   
    cdef int tileInW = tarW / tileW
    
    cdef int tileOut
    cdef int tileIn
    cdef int getInd
    cdef int bitOrigin
    cdef int bitSet
    
    cdef int picY
    cdef int picX
    
    if bpp == 1:
        # assert shift == 0 and mark == 0xff, 'Error fromTile'
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