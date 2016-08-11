#!/usr/bin/env python3
import os, re, argparse
import pandas as pd

# remove duplicate strings during renaming
def rm_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def rename(target_dir, assembly_summary_df):

    # clean up assembly_summary.txt

    assembly_summary_df.update(assembly_summary_df['infraspecific_name'][(assembly_summary_df['infraspecific_name'].isnull()) & (assembly_summary_df['isolate'].isnull())].fillna('NA'))
    assembly_summary_df.update(assembly_summary_df['infraspecific_name'][(assembly_summary_df['infraspecific_name'].isnull()) & (assembly_summary_df['isolate'].notnull())].fillna(assembly_summary_df['isolate']))
    assembly_summary_df.assembly_level.replace({' ': '_'}, regex=True, inplace=True)
    assembly_summary_df.organism_name.replace({' ': '_'}, regex=True, inplace=True)
    assembly_summary_df.organism_name.replace({'[\W]': '_'}, regex=True, inplace=True)
    assembly_summary_df.infraspecific_name.replace({'[\W]': '_'}, regex=True, inplace=True)

    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.startswith("GCA"):
                assembly_summary_id = "_".join(f.split('_')[0:2])
                if assembly_summary_id in assembly_summary_df.index:
                    org_name = assembly_summary_df.get_value(assembly_summary_id, 'organism_name')
                    strain = assembly_summary_df.get_value(assembly_summary_id, 'infraspecific_name')
                    assembly_level  = assembly_summary_df.get_value(assembly_summary_id, 'assembly_level')
                    new_name = '{}_{}_{}_{}.fasta'.format(assembly_summary_id, org_name, strain, assembly_level)
                    rm_words = re.compile( r'((?<=_)(sp|sub|substr|subsp|str|strain)(?=_))' )
                    new_name = rm_words.sub('_', new_name)
                    new_name = re.sub(r'_+', '_', new_name )
                    new_name = new_name.split('_')
                    new_name = rm_duplicates(new_name)
                    new_name = '_'.join(new_name)
                    old = os.path.join(root, f)
                    new = os.path.join(root, new_name)
                    os.rename(old, new)

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_dir', help = 'The folder whose contents will be renamed', type=str)
    parser.add_argument('-s', '--source', help = 'Specify a directory to rename.', action="store_true")
    args = parser.parse_args()

    rename(args.target_dir, assembly_summary_df)

if __name__ == '__main__':
    Main()
