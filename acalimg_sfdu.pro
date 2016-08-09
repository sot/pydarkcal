pro acalimg_sfdu, caldatafile, view

; Process ACA calibration data.
; Produce a data product in Level 0 ICD format.
;
; The input data are expected to be in SFDUs, 1134-bytes long,
; with 1 telemetry minor frame (or DSN record) per SFDU.
; The SFDU format is given in the ICD between JPL and MSFC.
;
; Robert Cameron
; April 1999

; TERMINOLOGY: a "segment" is where the 24-bit DSN record counter is contiguous
; (i.e. increments by 1 between DSN records)
; TERMINOLOGY: a "readout" is where the CCD row number is contiguous
; (i.e. increments or decrements by 1 between cal records)
; Generally, a DSN segment can contain multiple readouts,
; with DSN fill data between the readouts.
;
get_lun,il
get_lun,ol
get_lun,mytest

SFDUsync = byte('NJPL')
VCDUsync = ['1A'xb,'CF'xb,'FC'xb,'1D'xb]

DSNch = ['41'xb,'93'xb]

;filedir='/proj/telmon/tlm/raw/cal/'
;filedir='./'

sfdurecl = 1134  ; Number of bytes in an SFDU
sfduhdrl = 104   ; Number of bytes in SFDU header
dsnrecl = 1029   ; Number of bytes per truncated DSN record
calrecl = 1040   ; Number of bytes per cal record

cltick = 2d-6    ; 2 microsecond clock period
quadstr=['A','C','B','D']    ; quadrant identifiers for values of QUADID
;
; create a structure record of the L0 product type
;
sl0 ={ACAL0,TIME_ERT:0.0d0,REC_CTR:0L,ADC_BIAS:0,INTEG:0.0,CALTYPE:0,REPLICA:0,$
            COLNEG:0,ROW:0,SCI_HDR_CTR:0,TWO_US_CLK:0L,PIXDATA:intarr(512)}
sl0n=0
;
; start processing the cal data files
;
;file=dialog_pickfile(/must_exist,get_path=filedir,path=filedir,filter='*SFDU*',$
;                  title='Select an ACA darkcal file to read')
file = caldatafile
if file eq '' then stop, '% Try again, Bozo!'
;
openr,il,file
r=assoc(il,bytarr(sfdurecl))
openw,ol,'../data2/test_file_idl.txt'
openw,mytest,'../data2/my_test_idl.txt'
prb,ol, 'ACA cal data file: ',file
prb,ol,''
prb,ol,'Valid SFDU sync is: ',string(SFDUsync)
prb,ol,'Valid DSN record sync is: ',VCDUsync,DSNch,form='(a,6Z3.2)'
prb,ol,''
;
; count the number of records in the file
;
i=0L
v=0L
tdsn=0L
tfil=0L
tother=0L
nrecmax = 20000
idx=lonarr(nrecmax)
count=lonarr(nrecmax)
ert=dblarr(nrecmax)
timcount=0 ; a counter for composite total images written to FITS files
rotally=intarr(1024,2)
rofill=intarr(1024,2)
imarr=fltarr(1024,1024)
quadarr=fltarr(512,512)
quadfill=intarr(512)
quadtally=intarr(4)
prevquadid=-1
;
; Inspect each SFDU in the file and check its contents
;
on_ioerror,bad_io
while not eof(il) do begin
  valid_io = 0
  ir=r(i)
  valid_io = 1
  synctest1=ir(0:3)
  synctest2=ir(sfduhdrl+0:sfduhdrl+3)
  notexplained=1
  if not (total(synctest1-SFDUsync)+total(synctest2-VCDUsync)) then begin
; This SFDU starts with a correct sync pattern
;
    notexplained=0
    v=v+1L
    ch=ir(sfduhdrl+4:sfduhdrl+5)
;    if not total(ch-DSNch) then begin   ; the record is a "DSN record" from the ACA
    if not total(ch[1]-DSNch[1]) then begin   ; the record is a "DSN record" from the ACA ; kludge to get around a bad header byte
;
; test if the DSN record contains only fill data
;
      valid_io = 0
      testrec=ir
      valid_io = 1
      testr=where(testrec(sfduhdrl+10:sfduhdrl+1028) ne 170,testn)

      if testn gt 3 then begin  ; DSN minor frame contains non-fill data
        idx(tdsn)=i
        count(tdsn)=ir(sfduhdrl+6)*65536L+ir(sfduhdrl+7)*256L+ir(sfduhdrl+8)
;
; I will carry time since the start of 1998 (the Chandra FITS file reference)
; which is 14610 days after the start of 1958 (the ERT reference), in seconds.
; NOTE: I ignore the 32.182 second + leap seconds offset between UTC (for ERT) and TT (for FITS)
;
        ert(tdsn) = (ir(42)*256L + ir(43) - 14610) * 84600d0 + $
          (((ir(44)*256L + ir(45))*256L + ir(46))*256L + ir(47))/1d3 + (ir(48)*256L + ir(49))/1d6
        tdsn=tdsn+1L
      endif else tfil=tfil+1L    ; DSN minor frame contains only fill data
;      if (testrec(sfduhdrl+10) eq 170 and testrec(sfduhdrl+1028) eq 170) then begin
;        prb,ol,r(i-1),format='(42z3.2)'
;        prb,ol,r(i)  ,format='(42z3.2)'
;        prb,ol,r(i+1),format='(42z3.2)'
;        stop,'HERE WE GO!'
;      endif
    endif
    if total(ch-DSNch) then begin
      tother=tother+1L
      prb,ol,'record '+strtrim(i+1,2)+' has unknown VCID: ',ir(sfduhdrl+0:sfduhdrl+5),format='(a,6Z3.2)'
    endif
  endif
  i=i+1L
;
; I don't understand the start of the 1029-byte record at all!
;
  if notexplained then $
    prb,ol,' *** record '+strtrim(i,2)+' start is weird: ',ir(0:sfduhdrl+11),form='(a,19Z3.2)'
;
; try and gracefully get past incorrect file endings (e.g. incomplete records)
;
bad_io: if not valid_io then prb,ol,' >>>>>> Unexpected EOF of input file at record ',strtrim(i+1,2)
endwhile
prb,ol,''
prb,ol,tdsn,' DSN minor frames with pixel data in the file'
prb,ol,tfil,' FIL minor frames in the file'
prb,ol,tother,' OTHER minor frames in the file'
prb,ol,''
prb,ol,i,' SFDUs in the file'
prb,ol,''
if tdsn le 0 then begin
  prb,ol,'No DSN minor frames in the file, Bozo! I''m stopping!'
  stop
endif

idx=idx(0:tdsn-1)
count=count(0:tdsn-1)
ert = ert(0:tdsn-1)
;stop
;
; TERMINOLOGY: a "segment" is where the 24-bit DSN record counter is contiguous
; (i.e. increments by 1 between DSN records)
; extract the DSN record counter segments
; disc contains the first indices of new DSN segments
;
disc=where((count-shift(count,1)) ne 1,ndisc)

;  disc=where(abs(count-shift(count,1)) gt 5,ndisc)
disc=[disc,tdsn]

prb,ol,ndisc,' segments in the DSN minor frame counter'
;
; process each segment (i.e. contiguous set) of DSN records
;
for f=0,ndisc-1 do begin
  prb,ol,''
  prb,ol,'>>>>>>>>>>>>>>> Processing DSN record segment ',strtrim(f+1,2),' <<<<<<<<<<<<<<<'
  prb,ol,''
;; construct the DSN record array for this segment
;
  ndrec=disc(f+1)-disc(f)
  maindat=bytarr(1020,ndrec) ;1020 cols and 60 ndrec rows
  m=0L
  for j=disc(f),disc(f+1)-1 do begin
    k=idx(j)
    ir1=r(k)
    maindat(*,m)=ir1(sfduhdrl+9:sfduhdrl+1028)
    m=m+1L
  endfor

  scount=count(disc(f):disc(f+1)-1)
  sert=ert(disc(f):disc(f+1)-1)
  prb,ol,'first, last, delta in DSN minor frame counter:  ',strtrim(scount(0),2)$
     ,'  ',strtrim(scount(ndrec-1),2),'  ',strtrim(scount(ndrec-1)-scount(0)+1,2)
  prb,ol,'DSN secondary header range: ',$
         min(maindat(0,*)),max(maindat(0,*)),format='(a,2Z3.2)'
  prb,ol

;
; find the calibration data in the DSN records,
; which is differently placed in alternating DSN records.
; Test for both ways of packing.
;
  if ndrec eq 1 then begin
    prb,ol,'This is a single non-fill cal minor frame at record index ',strtrim(idx(disc(f))+1,2)
;    prb,ol,r(idx(disc(f))-1),format='(42z3.2)'
;    prb,ol,r(idx(disc(f)))  ,format='(42z3.2)'
;    prb,ol,r(idx(disc(f))+1),format='(42z3.2)'
    prb,ol
    prb,ol,'I''m OUTA HERE!'
;    stop
    goto, nextdisc
  endif
  ev=where((scount/2)*2 eq scount,nev)
  print,maindat(1,ev)
  stop
  od=where((scount/2)*2 ne scount,nod)

  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!
  ; PYTHON CODE STOPS WORKING HERE!!!

  if not (total(maindat(1,ev)-'cd'xb)+total(maindat(1019,od)-'ab'xb)) then calsync=0 $
  else if not (total(maindat(1,od)-'cd'xb)+total(maindat(1019,ev)-'ab'xb)) then calsync=1 $
  else prb,ol,'Cal data doesn''t sync to DSN minor frame counter! Using previous sync...'
  case calsync of
  0: begin
       prb,ol,'Cal records are synchronized to even DSN minor frame counter'
       maindat(0:1017,ev)=temporary(maindat(2:1019,ev))
       maindat(0:1017,od)=temporary(maindat(1:1018,od))
     end
  1: begin
       prb,ol,'Cal records are synchronized to odd DSN minor frame counter'
       maindat(0:1017,od)=temporary(maindat(2:1019,od))
       maindat(0:1017,ev)=temporary(maindat(1:1018,ev))
     end
  endcase
  maindat=temporary(maindat(0:1017,*))
  maindat=reform(maindat,n_elements(maindat))
;
; locate complete calibration records in the extracted cal data
; and check constancy of cal record size
;
  sync1=where(maindat eq 255)
  sync=sync1(where(maindat(sync1+1) eq 0 and maindat(sync1+14) eq 170 and maindat(sync1+15) eq 170))
  if n_elements(sync) le 1 then begin
    prb,ol,'I''m OUTA HERE! Because there are no complete cal records in this segment.'
    goto, nextdisc
  endif
  syncd=(sync-shift(sync,1))(1:*)
  bads=where(syncd ne calrecl,nbad)
  prb,ol,nbad,' calibration records of wrong size'
  if nbad gt 0 then begin
;
; check if bad record sizes are due to accidental sync patterns in good cal records
;
    if total(syncd(bads))/calrecl eq nbad/2 then nbad=0
    if nbad gt 0.05*ndrec then begin
      prb,ol,'Too many bad cal records! I''m OUTA HERE!'
      goto, nextdisc
    endif
    prb,ol,' *** Bad record numbers: ',bads
    prb,ol,' *** Bad record lengths: ',syncd(bads)
    bad1=where((maindat(0,*) ne 255) or (maindat(1,*) ne 0),nbad1)
    prb,ol,nbad1,' calibration records have wrong sync'
    if nbad1 gt 0 then begin
      prb,ol,' *** Bad record numbers: ',bad1
      prb,ol,' Bad sync patterns: ',maindat(0:1,bad1)
    endif
  endif
;
; truncate to an integral number of cal records, and reformat
;
  maindat = temporary(maindat(sync(0):*))
  nrec = n_elements(maindat)/calrecl
  maindat = temporary(maindat(0:nrec*calrecl-1))
  maindat = temporary(reform(maindat,calrecl,nrec))
  prb,ol
  prb,ol, nrec,' whole calibration records found'
;
; extract the DSN record counter and ERT fields
; from the DSN records containing the cal record syncs
;
  syncrecs = lonarr(nrec)
  for i=0L,nrec-1 do syncrecs(i)=(i*calrecl+sync(0)) / 1018
  scount=scount(syncrecs)
  sert=sert(syncrecs)
;
; get rid of the cal record syncs - we don't need them anymore
;
  maindat=temporary(maindat(2:*,*))
;
; do some more locating of incorrect sync patterns
;
  if nbad gt 0 then begin
    sync1=where(maindat eq 255)
    bad2=where(maindat(sync1+1) eq 0 and maindat(sync1+14) eq 170 and maindat(sync1+15) eq 170,nbad2)
    prb,ol,nbad2,' calibration records with badly placed sync'
    if nbad2 gt 0 then begin
      badsync=sync1(bad2)
      badrec=badsync/(calrecl-2)
      badbyte=badsync mod (calrecl-2)
      prb,ol,' *** Bad records: ',badrec
      prb,ol,' *** Bad record sync positions (bytes): ',badbyte
      for j=0,nbad2-1 do $
        prb,ol,' Bad record',badrec(j),' contents: ',$
          maindat(0:badbyte(j)+3,badrec(j)),form='(a,i6,a,100Z3.2)'
      rownum = (maindat(4,badrec) mod 8)*256 + maindat(5,badrec)
      neg = where(rownum ge 1024,nneg)
      if nneg gt 0 then rownum(neg) = rownum(neg) + 248*256
      prb,ol, ' Bad row numbers: ',reform(rownum)
    endif
  endif
;
; extract the calibration parameters and
; determine which cal records contain real data
;
  rownum = (maindat(4,*) mod 8)*256 + maindat(5,*)
  neg = where(rownum ge 1024,nneg)
  if nneg gt 0 then rownum(neg) = rownum(neg) + 248*256
  rdat = where(rownum(0,*) lt 600,nrdat)
  prb,ol
  if nrdat gt 1 then begin
    interup=rdat-shift(rdat,1)
    interup=interup(1:*)
    interupidx=where(interup gt 1,ninterup)
    prb,ol, nrdat,' real calibration records found'
    prb,ol, ninterup,' interruptions found among the cal records'
    if ninterup gt 0 then begin
      interups=median(interup(interupidx))
      interupp=median(interupidx-shift(interupidx,1))
      prb,ol,'median interruption duration (cal records): ',fix(interups)
      prb,ol,'median interruption interval (cal records): ',fix(interupp)
    endif
    prb,ol,''
    rownum = rownum(rdat)
    maindat = temporary(maindat(*,rdat))
    inttime = (maindat(2,*)*256L + maindat(3,*)) * 0.016
    bias = maindat(0,*)*256L + maindat(1,*)
    caltyp = (maindat(4,*) - (maindat(4,*) mod 128))/128
    replic = ((maindat(4,*) mod 128) - (maindat(4,*) mod 16))/16
    colpn = ((maindat(4,*) mod 16) - (maindat(4,*) mod 8))/8
    scifrmcnt = maindat(6,*)*256L + maindat(7,*)
    twousclk = (maindat(8,*)*256L + maindat(9,*))*65536L + $
                maindat(10,*)*256L + maindat(11,*)
    ftime = scifrmcnt*2.05 + twousclk*cltick
    scount = scount(rdat)
    sert = sert(rdat)
;
; TERMINOLOGY: a "readout" is where the CCD row number is contiguous
; (i.e. increments or decrements by 1 between cal records)
; find separate cal region readouts, indicated by discontinuities in row number
;
    reg=where(abs(rownum-shift(rownum,1)) ne 1,nreg)
    reg=[reg,nrdat]
    prb,ol,nreg,' separate readouts in the cal data'
;
; process each contiguous set of Cal records
;
    for rr=0,nreg-1 do begin
      prb,ol,''
      prb,ol,'  ====== Cal readout ',strtrim(rr+1,2),' information ======'
      prb,ol,''
      nrows=reg(rr+1)-reg(rr)
      prb,ol,nrows,' rows in readout'
      colpnr = colpn(reg(rr):reg(rr+1)-1)
      rownumr = rownum(reg(rr):reg(rr+1)-1)
      if min(colpnr) ne max(colpnr) or (min(rownumr) lt 0 and max(rownumr) ge 0) then $
         prb,ol,' *** Readout region crosses quadrant boundary! INCONCEIVABLE!!!'
      quadid=max(colpnr)*2
      if max(rownumr) ge 0 then quadid=quadid+1
      if quadid ne prevquadid and prevquadid ge 0 then begin
;
; show the previous quadrant image before going to the next quadrant
;
        quadtally(prevquadid)=quadtally(prevquadid)+1
        if (view eq 1) then begin
            window,1,xsi=512,ysi=512,$
              tit='CCD Quadrant Image '+quadstr(prevquadid)+strtrim(quadtally(prevquadid),2)
            tvscl, alog((quadarr<5000)>1)
        endif
        prevquadid=-1
        quadfill=intarr(512) ; zero the quadrant fill array
        quadarr=fltarr(512,512) ; zero the quadrant data array
      endif
;
; now that any possible conflict with data from the previous quadrant
; is removed, proceed with the normal data extraction
;
      pixdatr=lonarr(512,nrows)
      for j=0,511 do pixdatr(j,*)=maindat(2*j+14,reg(rr):reg(rr+1)-1)*256L $
                                 +maindat(2*j+15,reg(rr):reg(rr+1)-1)
      biasr = bias(reg(rr):reg(rr+1)-1)
      biasr = transpose(rebin(biasr,nrows,512,/sample))
      inttimer = inttime(reg(rr):reg(rr+1)-1)
      caltyper = caltyp(reg(rr):reg(rr+1)-1)
      replicar = replic(reg(rr):reg(rr+1)-1)
      if max(rownumr) lt 0 then absrownumr=-1-rownumr else absrownumr=rownumr
      quadfill(absrownumr)=1
      quadarr(*,absrownumr)=pixdatr-biasr
      prevquadid=quadid
      rotally(rownumr+512,colpnr)=rotally(rownumr+512,colpnr)+1
      rofill(rownumr+512,colpnr)=1
      if (max(colpnr) eq 1) then $
;        imarr(512:1023,rownumr+512) = reverse(pixdatr,1) else $
;        imarr(0:511, rownumr+512) = pixdatr
        imarr(512:1023,rownumr+512) = reverse(pixdatr-biasr,1) else $
        imarr(0:511,rownumr+512) = pixdatr-biasr
      scifrmcntr = scifrmcnt(reg(rr):reg(rr+1)-1)
      twousclkr = twousclk(reg(rr):reg(rr+1)-1)
      timer = twousclkr*cltick
      ftimer = scifrmcntr*2.05 + timer
      scountr = scount(reg(rr):reg(rr+1)-1)
      sertr = sert(reg(rr):reg(rr+1)-1)
;
; populate the L0 structure
;
      sl0r=replicate(sl0,nrows)
      for j=0,nrows-1 do sl0r(j)={acal0,sertr(j),scountr(j),biasr(0,j)-32768L,inttimer(j),$
        caltyper(j),replicar(j),colpnr(j),rownumr(j),scifrmcntr(j),twousclkr(j),pixdatr(*,j)-biasr(*,j)}
      if sl0n gt 0 then begin
        sl0t=[sl0t,sl0r]
        sl0n=sl0n+nrows
      endif else begin
        sl0t=sl0r
        sl0n=nrows
      endelse
;
; provide some information about the readout
;
      prb,ol,'DSN record counter range and delta:',min(scountr),max(scountr),max(scountr)-min(scountr)+1
      prb,ol,'ERT time range and delta (seconds):',min(sertr),max(sertr),max(sertr)-min(sertr)
      prb,ol,'Integration time range (seconds):',min(inttimer),max(inttimer)
      prb,ol,'Bias value range (counts):',min(biasr),max(biasr)
      prb,ol,'Calibration type range:',min(caltyper),max(caltyper)
      prb,ol,'Replica number range:',min(replicar),max(replicar)
      prb,ol,'CCD column sign range:',min(colpnr),max(colpnr)
      prb,ol,'CCD row number range and excursion:',$
                min(rownumr),max(rownumr),max(rownumr)-min(rownumr)+1
      prb,ol,'Science Frame Hdr count range:',min(scifrmcntr),max(scifrmcntr)
      prb,ol,'2-us clock word (32 bits):',min(twousclkr),max(twousclkr)
      prb,ol,'Time range and delta (seconds):',min(ftimer),max(ftimer),max(ftimer)-min(ftimer)
      prb,ol,'Pixel value range (counts):',min(pixdatr),max(pixdatr)
      prb,ol,'Bias-corrected pixel value range (counts):',min(pixdatr-biasr),max(pixdatr-biasr)
;
; display cal readout
;
      if (view eq 1) then begin
          window,xsi=512,ysi=nrows,$
            title='Segment/Readout: '+strtrim(f+1,2)+'/'+strtrim(rr+1,2)
;      tvscl, (pixdatr-biasr)<5000 & tvscl, (pixdatr-biasr)<5000
          tvscl, alog(((pixdatr-biasr)<5000)>1) & tvscl, alog(((pixdatr-biasr)<5000)>1)
      endif
;

; display full quadrant if available
;
      if min(quadfill) eq 1 then begin
        quadtally(quadid)=quadtally(quadid)+1
        if (view eq 1) then begin
            window,1,xsi=512,ysi=512,$
              tit='CCD Quadrant Image '+quadstr(quadid)+strtrim(quadtally(quadid),2)
            tvscl, alog((quadarr<5000)>1)
        endif
        prevquadid=-1
        quadfill=intarr(512) ; zero the quadrant fill array
        quadarr=fltarr(512,512) ; zero the quadrant data array
      endif
;
; display full focal plane if available
;
      if min(rofill) eq 1 then begin
        timcount=timcount+1
        if (view eq 1) then begin
            window,2,xsi=1024,ysi=1024,tit='Full CCD Image '+strtrim(timcount,2)
            tvscl, alog((imarr<5000)>1)
;        tvscl, imarr<5000
        endif
        rofill=intarr(1024,2)   ; zero the fill array
        imarr=fltarr(1024,1024) ; zero the data array
      endif
    endfor      ; end of cal readout region loop
  endif else begin
    prb,ol, 'No valid data!'
    maindat=0
  endelse
nextdisc: f=f+0
endfor     ; end of DSN record segment loop. No more data!
;
; display quadrant image if at all populated
;
if max(quadfill) gt 0 then begin
  quadtally(quadid)=quadtally(quadid)+1
  if (view eq 1) then begin
      window,1,xsi=512,ysi=512,$
        tit='CCD Quadrant Image '+quadstr(quadid)+strtrim(quadtally(quadid),2)
      tvscl, alog((quadarr<5000)>1)
  endif
  prevquadid=-1
  quadfill=intarr(512) ; zero the quadrant fill array
  quadarr=fltarr(512,512) ; zero the quadrant data array
endif
;
; give cal readout statistics
;
prb,ol,''
prb,ol,fix(total(rotally)),' rows read from CCD in total'
prb,ol, min(rotally),' is the minimum row repeat count'
prb,ol, 'Row readout histogram: '
rohist=histogram(rotally)
for h=0,n_elements(rohist)-1 do $
  prb,ol,'Number of readouts:',h+min(rotally),'     Number of rows:',rohist(h)
;
; display full focal plane image if at all populated
;
if max(rofill) gt 0 then begin
    timcount=timcount+1
    if (view eq 1) then begin
        window,2,xsi=1024,ysi=1024,tit='Full CCD Image '+strtrim(timcount,2)
        tvscl, alog((imarr<5000)>1)
    endif
;   tvscl, imarr<5000
endif
;
; write the pseudo-Level0 telemetry product FITS file
;
l0name=file+'-L0.fits'
phdr = [$
;         1         2         3         4         5         6         7         8
;12345678901234567890123456789012345678901234567890123456789012345678901234567890
"EXTEND  =                    T / FITS dataset may contain extensions            ",$
"COMMENT   FITS (Flexible Image Transport System) format defined in Astronomy and",$
"COMMENT   Astrophysics Supplement Series v44/p363, v44/p371, v73/p359, v73/p365.",$
"COMMENT   Contact the NASA Science Office of Standards and Technology for the   ",$
"COMMENT   FITS Definition document #100 and other FITS information.             ",$
"COMMENT                                                                         ",$
"COMMENT   *************** Description ****************************              ",$
"COMMENT                                                                         ",$
"COMMENT      This file is an ASC Level 0 data product.                          ",$
"COMMENT      It contains the unpacked AXAF telemetry data.                      ",$
"COMMENT                                                                         ",$
"COMMENT   *************** AXAF Header ****************************              ",$
"COMMENT                                                                         ",$
"MISSION = 'AXAF    '           / Advanced X-Ray Astrophysics Facility           ",$
"TELESCOP= 'CHANDRA '           / Telescope used                                 ",$
"DATACLAS= 'OBSERVED'           / Observed or Simulated                          ",$
"COMMENT                                                                         ",$
"COMMENT   *************** Time Information ***********************              ",$
"COMMENT                                                                         ",$
"DATE    = '1998-12-18T22:29:19' / Date and time of file creation (UTC)          ",$
"MJDREF  = 5.08140000000000E+04 / Modified Julian Day reference time             ",$
"TIMESYS = 'TT      '           / Time system                                    ",$
"TIMEUNIT= 's       '           / Unit for time measures                         ",$
"TSTART  = 3.10062500000000E+02 / Data file start time                           ",$
"TSTOP   = 4.36393750000000E+02 / Data file stop time                            ",$
;"COMMENT                                                                         ",$
;"COMMENT   *************** Start/Stop Counters ********************              ",$
;"COMMENT                                                                         ",$
;"COMMENT   These counters pertain to the data contained within this              ",$
;"COMMENT   data file and reflect the start and stop positions within             ",$
;"COMMENT   the raw telemetry stream where this data occurred. This               ",$
;"COMMENT   information is intended to provide mapping between the                ",$
;"COMMENT   decommed Level 0 data products and its source data contained          ",$
;"COMMENT   in the raw telemetry data files. This information is used             ",$
;"COMMENT   for recovery processing and reprocessing purposes.                    ",$
;"COMMENT                                                                         ",$
;"STARTMRF=                    0 / Major frame roll ctr at start of data          ",$
;"STARTMJF=                    9 / Major frame ctr value at start of data         ",$
;"STARTMNF=                   58 / Start minor frame ctr at start of data         ",$
;"STOPMRF =                    0 / Major frame roll ctr at stop of data           ",$
;"STOPMJF =                   13 / Major frame ctr value at stop of data          ",$
;"STOPMNF =                  166 / Stop minor frame ctr at end of data            ",$
"COMMENT                                                                         ",$
"COMMENT   *************** Telemetry Format Id ********************              ",$
"COMMENT                                                                         ",$
"TLM_FMT =                    0 / Format in which this data was telemetered      ",$
"COMMENT                                                                         ",$
"COMMENT                          0 - ACA Calibration Dump                       ",$
"COMMENT                          1 - HRC Science Data                           ",$
"COMMENT                          2 - ACIS Science Data                          ",$
"COMMENT                          3 - OBC Dump Data                              ",$
"COMMENT                          4 - Engineering Only                           ",$
"COMMENT                          5 - Programmable                               ",$
"COMMENT                          6 - STS Deployment                             ",$
"COMMENT                          8 - EEPROM Dump                                ",$
"END                                                                             "]
exthdr = [$
"EXTNAME = 'ACA_DUMP'           / ACA Calibration Data                           ",$
"COMMENT                                                                         ",$
"CREATOR = 'ACALIMG_SFDU'       / IDL procedure which created this FITS file     ",$
"ORIGIN  = 'ASC     '           / Origin of FITS file                            ",$
"DATE    = '1998-12-18T22:29:19' / Date and time of file creation (UTC)          ",$
;"COMMENT                                                                         ",$
;"COMMENT   ****************     Binary Data Format     ****************          ",$
;"COMMENT                                                                         ",$
;"TTYPE1  = 'TIME_ERT'           / Time-tag of the data record                    ",$
;"TFORM1  = '1D      '           / data format of field: 8-byte DOUBLE            ",$
;"TUNIT1  = 's       '           / physical unit of field                         ",$
;"TTYPE2  = 'REC_CTR '           / 24-bit record counter, from ACA DSN records    ",$
;"TFORM2  = '1J      '           / data format of field: 4-byte INTEGER           ",$
;"TLMIN2  =		      0 / Minimum field value                            ",$
;"TLMAX2  =             16777215 / Maximum field value                            ",$
;"TTYPE3  = 'ADC_BIAS'           / A/D converter offset                           ",$
;"TFORM3  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TZERO3  =                32768 / offset for unsigned integers                   ",$
;"TSCAL3  =                    1 / data are not scaled                            ",$
;"TUNIT3  = 'DN      '           / physical unit of field                         ",$
;"TTYPE4  = 'INTEG   '           / integration time                               ",$
;"TFORM4  = '1E      '           / data format of field: 4-byte REAL              ",$
;"TUNIT4  = 's       '           / physical unit of field                         ",$
;"TTYPE5  = 'CALTYPE '           / calibration type flag                          ",$
;"TFORM5  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TTYPE6  = 'REPLICA '           / replica value                                  ",$
;"TFORM6  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TTYPE7  = 'COLNEG  '           / columns negative                               ",$
;"TFORM7  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TTYPE8  = 'ROW     '           / CCD row number                                 ",$
;"TFORM8  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TTYPE9  = 'SCI_HDR_CTR'        / Science header pulse counter                   ",$
;"TFORM9  = '1I      '           / data format of field: 2-byte INTEGER           ",$
;"TTYPE10 = 'TWO_US_CLK'         / Two microsecond clock count                    ",$
;"TFORM10 = '1J      '           / data format of field: 4-byte INTEGER           ",$
;"TTYPE11 = 'PIXDATA '           / Pixel data for 1 CCD row                       ",$
;"TFORM11 = '512I    '           / data format of field: 2-byte INTEGER           ",$
;"TUNIT11 = 'DN      '           / physical unit of field                         ",$
"END										 "]
mwrfits,dummyvar,l0name,phdr,/create
mwrfits,sl0t,l0name,exthdr
prb,ol
prb,ol,'L0 data product written to ',l0name
close,ol
free_lun,il
free_lun,ol
end
