#import numpy as np
import sys
import struct
from variables import *

#pro prb, olun,a,b,c,...,z,format=fmt
def prb(olun,param_array,fmt):
    str = ' '.join(param_array)
    if fmt != '':
        str = str
        #',format=\'' + fmt + '\''
    print(str)
    olun.write(str + '\n')


#caldatafile: data file to call
#view number: 0 or 1
#acalimg_sfdu(caldatafile,view)
data_file = sys.argv[1] #caldatafile
if data_file == '':
    print('ERROR: -> data_file: ' + data_file)

'''
OPEN DATA_FILE to Read and Write
'''

f = open(data_file,'r+b')
il = f.read()
f.close()
ol = open(data_file + '.anal','w')

"""
Print to anal file
"""
prb(ol,['ACA cal data file:',data_file],'')
prb(ol,'','')
prb(ol,['Valid SFDU sync is:',str(SFDUsync)],'')
prb(ol,['Valid DSN record sync is:',str(VCDUsync),str(DSNch)],'(a,6z3.2)')
prb(ol,'','')


"""
r = array struct with 'unit' il and array_struct 104
Looping through r(i) #i+=1 at end of loop

"""

try:
    for ir in il:
        valid_io = 0 #NOTE: USED AT THIS TIME, ONCE CONFIRMED USELESS, DELETE
        valid_io = 1 #NOTE: USED AT THIS TIME, ONCE CONFIRMED USELESS, DELETE
        synctest1 = ir[0:3]
        synctest2 = ir[sfduhdrl:sfduhdrl+3]
        print synctest1
        print synctest2

        #if not (total(synctest1-SFDUsync)+total(synctest2-VCDUsync)) then begin
        #if not 0<false> then begin
        #if total+total != 0 then begin
        if ( sum(synctest1-SFDUsync) + sum(synctest2-VCDUsync) != 0 ):
            print 'inside: if ( sum(synctest1-SFDUsync) + sum(synctest2-VCDUsync) != 0 ):...'


except IOError:
    print prb(ol,[' >>>>>> Unexpected EOF of input file at record ',str(i+1)],'')


'''
prb(ol,'','')
prb(ol,[tdsn,' DSN minor frames with pixel data in the file'],'')
prb(ol,[fil,' FIL minor frames in the file'],'')
prb(ol,[tother,' OTHER minor frames in the file'],'')
prb(ol,'','')
prb(ol,[i,' SFDUs in the file'],'')
prb(ol,'','')
'''

ol.close()
