# -*- coding: utf-8 -*-
"""
Created on Wed Jul 03 12:31:35 2013

@author: Stardrad
"""
import os
def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            yield os.path.join(root, name)
            
for curName in walk('.'):
    fName = curName[curName.rindex('\\') + 1:]
    if '.' in fName:
        print 'pass %s' % fName
        continue
    else:
        os.rename(curName, curName + '.bin')
        print 'fix %s' % curName[:-4]