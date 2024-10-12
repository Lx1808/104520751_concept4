import re
from collections import *
import os
import pandas as pd


#Get the opcode sequence
def getOpcodeSequence(filename):
    opcode_seq = []
    p = re.compile(r'\s([a-fA-F0-9]{2}\s)+\s*([a-z]+)')
    with open(filename, mode="r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith(".text"):
                m = re.findall(p, line)
                if m:
                    opc = m[0][1]
                    if opc != "align":
                        opcode_seq.append(opc)
    return opcode_seq


#Slice the opcode sequence into units of 3 opcodes and count each unit sequence
def getOpcodeNgram(ops, n=3):
    opngramlist = [tuple(ops[i:i + n]) for i in range(len(ops) - n)]
    opngram = Counter(opngramlist)
    return opngram


basepath = "/malware_class/subtrain"
map3gram = defaultdict(Counter)
subtrain = pd.read_csv('/malware_class/subtrain_label.csv')
count = 1

# Get the n-gram features of each file and store them in map3gram
for sid in subtrain.Id:
    print("counting the 3-gram of the {0} file...".format(str(count)))
    count += 1
    filename = basepath + sid + ".asm"
    ops = getOpcodeSequence(filename)
    op3gram = getOpcodeNgram(ops)
    map3gram[sid] = op3gram

#Get the total n-gram features, calculate their occurrence times, and store the units with occurrence times greater than 500 in selectedfeatures for later processing
cc = Counter([])
for d in map3gram.values():
    print(d)
    cc += d
selectedfeatures = {}
tc = 0
for k, v in cc.items():
    if v >= 500:
        selectedfeatures[k] = v
        print(k, v)
        tc += 1

dataframelist = []
# The n-gram feature of each file is a row in dataframelist, and each column is the number of occurrences of each unit.
for fid, op3gram in map3gram.items():
    standard = {}
    standard["Id"] = fid
    for feature in selectedfeatures:
        if feature in op3gram:
            standard[feature] = op3gram[feature]
        else:
            standard[feature] = 0
    dataframelist.append(standard)

df = pd.DataFrame(dataframelist)
df.to_csv("/malware_class/3gramfeature.csv", index=False)
