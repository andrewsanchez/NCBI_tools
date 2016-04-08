#!/usr/bin/env python

import os
import sys
import pandas as pd

fastas = sys.argv[1] # folder containing all fastas, e.g. genbank_bacteria_fastas
summary = sys.argv[2] # location of assembly_summary.txt
df = pd.read_csv(summary, delimiter='\t', index_col=0)

total_fastas = []
correctly_named = []
misnamed = []
case_mismatch = []

for root, dirs, files in os.walk(fastas):
    for name in files:
        total_fastas.append(name)
        abs_path = os.path.join(root, name)
        fasta = open(abs_path, 'r')
        line = fasta.readline()
        genus = name.split('_')[2:3]
        genus_lower = genus[0].lower()
        genus_upper = genus[0].upper()
        species = name.split('_')[3:4]

        if genus[0] in line:
            correctly_named.append(name)
            fasta.close()
        elif genus_lower or genus_upper in line:
            case_mismatch.append(name)
            fasta.close()
        else:
            file = os.path.join(root, name)
            misnamed.append(file)
            fasta.close()

print('Total number of files:  {}'.format(len(total_fastas)))
print('Correctly named files:  {}'.format(len(correctly_named)))
print('Case mismatches:  {}'.format(len(case_mismatch)))
print('Misnamed files:  {}'.format(len(misnamed)))
print('\n')

missing = []

for f in misnamed:
    id = f.split('/')[2]
    id = (id.split('_')[0:2])
    id = ('_'.join(id))
    print(id)
    if id in df.index:
        with open(f, 'r') as fasta:
            line = fasta.readline()
            print(f)
            print(line)
        print(df.loc[id][6])
        print('\n')
    else:
        missing.append(f)
print(str(len(missing)) + ' files missing from assembly_summary.txt')
