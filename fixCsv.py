# -*- coding: utf-8 -*-
"""
Created on Wed Jul 03 12:46:29 2013

@author: Stardrad
"""

import csv,os,fnmatch

def walk(adr):
    #root,dirs,files = os.walk(adr).next()
    for root,dirs, files in os.walk(adr):
        for name in files:
            if fnmatch.fnmatch(name, '*.csv'):
                yield os.path.join(root, name)

for curName in walk('.'):
    with open(curName, 'rb') as csvfile:
        rd = csv.reader(csvfile)
        writeRows = []
        for row in rd:
            inCurName = row[0]
            fName = inCurName[inCurName.rindex('/') + 1:]
            if '.' in fName:
                pass
            else:
                row[0] = row[0]+'.bin'
            row[3] = 'Compress'
            writeRows.append(row)
    with open(curName, 'wb') as csvfile:
        wt = csv.writer(csvfile)
        wt.writerows(writeRows)
    print 'Proceed %s' % curName