import numpy as np
from astropy.io import fits

def split_header(header_string, length=80):
    return [header_string[i:i+length] for i in range(0, len(header_string), length)]


def compare_header_text(header1, header2):
    h1 = header1.tostring()
    h2 = header2.tostring()

    h1_lines = split_header(h1)
    h2_lines = split_header(h2)

    for h1_line, h2_line in zip(h1_lines, h2_lines):
        if h1_line != h2_line:
            print "H1: {}".format(h1_line)
            print "H2: {}".format(h2_line)


original = fits.open('/proj/sot/ska/data/aca_dark_cal/2016125/2016_125_VC2_Replica2_SFDU_31088-L0.fits')

to_check = fits.open('/home/jeanconn/Downloads/2016_125_VC2_Replica2_SFDU_31088-L0.fits')


print "Checking first hdu header lines"
compare_header_text(original[0].header, to_check[0].header)
print "Checking second hdu header lines"
compare_header_text(original[1].header, to_check[1].header)

print "Checking file data in all cols but PIXDATA"
o_data = original[1].data
n_data = to_check[1].data
cols = o_data.dtype.names
# the PIXDATA column in the data is the only one that has two dimensions, so handle that differently
for col in cols:
    if col == 'PIXDATA':
        continue
    for o_val, n_val in zip(o_data[col], n_data[col]):
        if o_val != n_val:
            print "orig: {}".format(o_val)
            print "new : {}".format(n_val)

print "Checking data in PIXDATA col"
for o_row, n_row in zip(o_data['PIXDATA'], n_data['PIXDATA']):
    if not np.all(o_row == n_row):
        mismatch = o_row != n_row
        print "mismatch {} {}".format(o_row[mismatch], n_row[mismatch])

print "Done"
