import numpy as np

#get_lun,il
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#get_lun,ol
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME

#SFDUsync = byte('NJPL')
SFDUsync = [78,  74,  80,  76]
#VCDUsync = ['1A'xb,'CF'xb,'FC'xb,'1D'xb]
VCDUsync = [26,207,252,29]
#DSNch = ['41'xb,'93'xb]
DSNch = [65,147]


#sfdurecl = 1134  ; Number of bytes in an SFDU
sfdurecl = 1134
#sfduhdrl = 104   ; Number of bytes in SFDU header
sfduhdrl = 104

#dsnrecl = 1029   ; Number of bytes per truncated DSN record
dsnrecl = 1029

#calrecl = 1040   ; Number of bytes per cal record
calrecl = 1040


#cltick = 2d-6    ; 2 microsecond clock period
cltick=2e-6
#TODO: FIGURE OUT WHAT '2d' IS

#quadstr=['A','C','B','D']    ; quadrant identifiers for values of QUADID
quadstr = ['A','C','B','D']


#sl0 ={ACAL0,TIME_ERT:0.0d0,REC_CTR:0L,ADC_BIAS:0,INTEG:0.0,CALTYPE:0,REPLICA:0,$
#            COLNEG:0,ROW:0,SCI_HDR_CTR:0,TWO_US_CLK:0L,PIXDATA:intarr(512)}
sl0 = {
    'TIME_ERT':0.0,
    'REC_CTR':0L,
    'ADC_BIAS':0,
    'INTEG':0.0,
    'CALTYPE':0,
    'REPLICA':0,
    'COLNEG':0,
    'ROW':0,
    'SCI_HDR_CTR':0,
    'TWO_US_CLK':0L,
    'PIXDATA':[None]*512
}

#sl0n=0
sl0n=0

#i=0L
indexo=0 # Named indexo so it is not confused with "i" or "index"
#v=0L
v=0
#tdsn=0L
tdsn=0
#tfil=0L
tfil=0
#tother=0L
tother=0
#nrecmax = 20000
nrecmax=20000
#idx=lonarr(nrecmax)
idx = []
#count=lonarr(nrecmax)
count = []
#ert=dblarr(nrecmax)
ert = []
#timcount=0 ; a counter for composite total images written to FITS files
timecount=0
#rotally=intarr(1024,2)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#rofill=intarr(1024,2)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#imarr=fltarr(1024,1024)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#quadarr=fltarr(512,512)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#quadfill=intarr(512)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#quadtally=intarr(4)
#NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
#prevquadid=-1
prevquadid=-1
