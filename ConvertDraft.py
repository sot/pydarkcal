import sys
from variables import *

#pro prb, olun,a,b,c,...,z,format=fmt
def prb(olun,param_array):
    str = ' '.join(param_array)
    print(str)
    olun.write(str + '\n')


def total(array_1,array_2,operator):
    array_return = []
    for i in range(4):
        if operator == '-':
            array_return.append( array_1[i] - array_2[i] )
        if operator == '+':
            array_return.append( array_1[i] + array_2[i] )
    return array_return


#caldatafile: data file to call
#view number: 0 or 1
#acalimg_sfdu(caldatafile,view)
data_file = sys.argv[1] #caldatafile
if data_file == '':
    print('ERROR: -> data_file: ' + data_file)


f = open(data_file,'r+b')
il = f.read()
f.close()
ol = open(data_file + '.anal','w')
ot = open('test_file_1.txt','w')


prb(ol,['ACA cal data file:',data_file])
prb(ol,'')
prb(ol,['Valid SFDU sync is:',str(SFDUsync)])
prb(ol,['Valid DSN record sync is:',str(VCDUsync),str(DSNch)])
prb(ol,'')


r = []
for i in range(len(il)/sfdurecl):
    r.append( il[i*sfdurecl:i*sfdurecl+sfdurecl] )


for rr in r:
    ir = []
    for rrr in rr:
        ir.append(ord(rrr))

    synctest1 = []
    synctest2 = []
    synctest1.append(ir[0])
    synctest1.append(ir[1])
    synctest1.append(ir[2])
    synctest1.append(ir[3])
    synctest2.append(ir[sfduhdrl+0])
    synctest2.append(ir[sfduhdrl+1])
    synctest2.append(ir[sfduhdrl+2])
    synctest2.append(ir[sfduhdrl+3])
    notexplained=1
    if total( total(synctest1,SFDUsync,'-') , total(synctest2,VCDUsync,'-') , '+') == [0,0,0,0]:
        notexplained=0
        v=v+1
        ch=[]
        ch.append(ir[sfduhdrl+4])
        ch.append(ir[sfduhdrl+5])
        if ch[1] - DSNch[1] == 0:
            testr = []
            for i in range(10,1028):
                testr.append( ir[sfduhdrl+i])
            testn=[]
            for n in testr:
                if n!=170:
                    testn.append(n)
            if testn > 3:
                idx[tdsn]=indexo #TODO: Fix Error, tdsn is out od range for idx index
                count[tdsn] = ir[sfduhdrl+6]*65536L+ir[sfduhdrl+7]*256L+ir[sfduhdrl+8]

                ert[tdsn] = (ir[42]*256L + ir[43] - 14610)* 84600**0+ (((ir[44]*256 + ir[45])*256 + ir[46])*256 + ir[47])/1**3+ (ir[48]*256 + ir[49])/1**6
                tdsn=tdsn+1

            else:
                tfil=tfil+2

        elif total(ch,DSNch,'-'):
            tother=tother+1
            prb(ol,['record',`i+1`,' has unknown VCID: ',ir[sfduhdrl:sfduhdrl+5]],'')
    i=i+1

    if notexplained==1:
        prb(ol,[' *** record ',`i`, 'start is weird: ',ir[0:sfduhdrl+11]])

#End of Loop


prb(ol,'')
prb(ol,[tdsn,' DSN minor frames with pixel data in the file'])
prb(ol,[fil,' FIL minor frames in the file'])
prb(ol,[tother,' OTHER minor frames in the file'])
prb(ol,'')
prb(ol,[i,' SFDUs in the file'])
prb(ol,'')


ol.close()
