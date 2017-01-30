#!/usr/bin/env python

import os, argparse, gzip
import pandas as pd
import tarfile
from urllib.request import urlretrieve
from urllib.error import URLError
from ftplib import FTP, error_temp
from time import strftime, sleep
from glob import glob
from re import sub

def grab_zipped_genome(genbank_mirror, species, genome_id, genome_url, ext=".fna.gz"):

    """
    Download compressed genome from ftp://ftp.ncbi.nlm.nih.gov/genomes/all/
    """

    zipped_path = "{}_genomic{}".format(genome_id, ext)
    zipped_url = "{}/{}".format(genome_url, zipped_path)
    zipped_dst = os.path.join(genbank_mirror, species, zipped_path)
    urlretrieve(zipped_url, zipped_dst)

def unzip_genome(root, f, genome_id):

    """
    Decompress genome and remove the compressed genome.
    """

    zipped_src = os.path.join(root, f)
    zipped = gzip.open(zipped_src)
    decoded = zipped.read()
    unzipped = "{}.fasta".format(genome_id)
    unzipped = os.path.join(root, unzipped)
    unzipped = open(unzipped, "wb")
    unzipped.write(decoded)
    zipped.close()
    unzipped.close()
    os.remove(zipped_src)

def unzip_genbank_mirror(genbank_mirror):

    for root, files, dirs, in os.walk(genbank_mirror):
        for f in files:
            if f.endswith("gz"):
                genome_id = "_".join(f.split("_")[:2])
                unzip_genome(root, zipped_src, genome_id)

def get_genome_id_and_url(assembly_summary, accession):

    genome_id = assembly_summary.ftp_path[accession].split('/')[-1]
    genome_url = assembly_summary.ftp_path[accession]

    return genome_id, genome_url


def sync_latest_genomes(genbank_mirror, assembly_summary, names):

        # local_genome_ids = get_local_genome_ids(species_dir)
        # if genome_id not in local_genome_ids:
    genbank_stats = os.path.join(genbank_mirror, 'stats.log')

    for accession in assembly_summary.index:
        genome_id, genome_url = get_genome_id_and_url(assembly_summary, accession)
        taxid = assembly_summary.species_taxid.loc[accession]
        species = names.species.loc[taxid]
        try:
            grab_zipped_genome(genbank_mirror, species, genome_id, genome_url)
        except URLError:
            grab_zipped_genome(genbank_mirror, species, genome_id, genome_url, ext=".fasta.gz")
        except URLError:
            with open(genbank_stats, "a") as stats:
                stats.write("URLError for {}\n".format(genome_id))
        print("Download {}".format(genome_url))
        with open(genbank_stats, "a") as stats:
            stats.write("{} downloaded\n".format(genome_id))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("genbank_mirror", help = "Directory to save fastas", type=str)
    parser.add_argument("-u", "--unzip", action="store_true")
    args = parser.parse_args()
    genbank_mirror = args.genbank_mirror

    assembly_summary = get_assembly_summary(genbank_mirror, assembly_summary_url="ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt")
    unzip_genbank_mirror(genbank_mirror)
    rename(genbank_mirror, assembly_summary)

if __name__ == "__main__":
    main()
