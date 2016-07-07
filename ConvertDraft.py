import sys
from variables import *

# TODO: Delete This when done
# Checks the dec value of a hex.
#i = int('48', 16)
#print 'segments in the DSN minor frame counter, Target: ' + repr(i)

# pro prb, olun,a,b,c,...,z,format=fmt
def prb(olun, param_array):
    str = ' '.join(param_array)
    print(str)
    olun.write(str + '\n')


# caldatafile: data file to call
# view number: 0 or 1
# acalimg_sfdu(caldatafile,view)
data_file = sys.argv[1]  # caldatafile
if data_file == '':
    print('ERROR: -> data_file: ' + data_file)


f = open(data_file, 'r+b')
il = f.read()
f.close()
ol = open('../data2/test_file_python.txt', 'w')


prb(ol, ['ACA cal data file:', data_file])
prb(ol, '')
prb(ol, ['Valid SFDU sync is:', str(SFDUsync)])
prb(ol, ['Valid DSN record sync is:', str(VCDUsync), str(DSNch)])
prb(ol, '')


r = []
for i in range(len(il)/sfdurecl):
    r.append(il[i*sfdurecl:i*sfdurecl+sfdurecl])


for rr in r:
    ir = []
    for rrr in rr:
        ir.append(ord(rrr))

    synctest1 = ir[0:4]
    synctest2 = ir[sfduhdrl:sfduhdrl+4]
    notexplained = 1

    if (synctest1 == SFDUsync and synctest2 == VCDUsync):
        notexplained = 0
        v = v+1
        ch = ir[sfduhdrl+4:sfduhdrl+6]
        if ch[1] == DSNch[1]:

            testr = [i for i in ir[sfduhdrl+10:sfduhdrl+1029] if i != 170]
            testn = len(testr)

            if testn > 3:
                idx.append(indexo)
                count.append(ir[sfduhdrl+6]*65536+ir[sfduhdrl+7]*256+ir[sfduhdrl + 8])
                ert.append((ir[42]*256 + ir[43] - 14610) * 84600e0 + (((ir[44] * 256 + ir[45])*256 + ir[46])*256 + ir[47])/1e3 + (ir[48]*256 + ir[49])/1e6)
                tdsn = tdsn+1

            else:
                tfil=tfil+1

        if ch!=DSNch:
            tother=tother+1
            prb(ol,['record',`i+1`,' has unknown VCID: ',' '.join(str(x) for x in ir[sfduhdrl:sfduhdrl+6])])

    indexo=indexo+1
    if notexplained==1:
        prb(ol,[' *** record ',`i`, 'start is weird: ',' '.join(ir[0:sfduhdrl+12])])

#End of Loop


prb(ol,'')
prb(ol,[`tdsn`,' DSN minor frames with pixel data in the file'])
prb(ol,[`tfil`,' FIL minor frames in the file'])
prb(ol,[`tother`,' OTHER minor frames in the file'])
prb(ol,'')
prb(ol,[`indexo`,' SFDUs in the file'])
prb(ol,'')

if tdsn <= 0:
    prb(ol,['No DSN minor frames in the file, Bozo! I''m stopping!'])

idx = idx[0:tdsn]
count = count[0:tdsn]
ert = ert[0:tdsn]

#disc=where((count-shift(count,1)) ne 1,ndisc)
disc = [i for i in (count - np.roll(count,1)) if i != 1]
ndisc = len(disc)
disc = [disc,tdsn]

prb(ol,[`ndisc`,'segments in the DSN minor frame counter'])


ol.close()
