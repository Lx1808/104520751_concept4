import os
import numpy
from collections import *
import pandas as pd
import binascii


def getMatrixfrom_asm(filename, startindex=0, pixnum=5000):
    with open(filename, 'rb') as f:
        f.s(startindex, 0)
        content = f.read(pixnum)
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i + 2], 16) for i in range(0, len(hexst), 2)])
    fh = numpy.uint8(fh)
    return fh


basepath = "/malware_class/subtrain"
mapimg = defaultdict(list)
subtrain = pd.read_csv('/malware_class/subtrain_label.csv')
i = 0
for sid in subtrain.Id:
    i += 1
    print("dealing with {0}th file...".format(str(i)))
    filename = basepath + sid + ".asm"
    im = getMatrixfrom_asm(filename, startindex=0, pixnum=1500)
    mapimg[sid] = im

dataframelist = []
for sid, imf in mapimg.items():
    standard = {}
    standard["Id"] = sid
    for index, value in enumerate(imf):
        colName = "pix{0}".format(str(index))
        standard[colName] = value
    dataframelist.append(standard)

df = pd.DataFrame(dataframelist)
df.to_csv("/malware_class/imgfeature.csv", index=False)
