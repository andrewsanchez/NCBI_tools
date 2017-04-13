#!/usr/bin/env python

import os
import argparse
import logging

from NCBITK import config
from NCBITK import sync
from NCBITK import curate
from NCBITK import get_resources
from NCBITK import rename

def setup(genbank_mirror, species_list, update_assembly_summary):

    path_vars = config.instantiate_path_vars(genbank_mirror)
    info_dir, slurm, out, logger = path_vars
    assembly_summary = get_resources.get_resources(genbank_mirror, logger, fetch_new)
    logger.info('{} genomes in assembly_summary.txt'.format(len(assembly_summary)))
    species = curate.get_species_list(assembly_summary, species_list)

    return path_vars, assembly_summary, species

def assess_genbank(genbank_mirror, assembly_summary, species_list, logger):

    genbank_status = curate.assess_genbank_mirror(genbank_mirror, assembly_summary, species_list)
    local_genomes, new_genomes, old_genomes, sketch_files, missing_sketch_files = genbank_status

    logger.info("{} genomes present in local collection.".format(len(local_genomes)))
    logger.info("{} genomes missing from local collection.".format(len(new_genomes)))
    if len(new_genomes) == 0:
        logger.info("Local collection is up to do with latest assembly summary file.")
    logger.info('{} sketch files present in local collection.'.format(len(sketch_files)))
    logger.info('{} sketch files not in local collection.'.format(len(missing_sketch_files)))

    return genbank_status

def update(genbank_mirror, genbank_status, path_vars, assembly_summary, species_list):

    info_dir, slurm, out, logger = path_vars
    curate.create_species_dirs(genbank_mirror, assembly_summary, logger, species_list)
    local_genomes, new_genomes, old_genomes, sketch_files, missing_sketch_files = genbank_status

    curate.remove_old_genomes(genbank_mirror, assembly_summary, local_genomes, logger)
    sync.sync_latest_genomes(genbank_mirror, assembly_summary, new_genomes, logger)
    curate.unzip_genbank_mirror(genbank_mirror)
    rename.rename(genbank_mirror, assembly_summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("genbank_mirror", help = "Directory to save fastas", type=str)
    parser.add_argument("-s", "--species", help = 'List of species', nargs='+', default='all')
    parser.add_argument("-p", "--slurm", help = 'Submit jobs in parallel via SLURM pipeline tool.', action="store_true")
    parser.add_argument("-u", "--update", action="store_true")
    parser.add_argument("--use_local", help = 'Use local copy new assembly_summary.txt and names.dmp', action="store_true", default=False)
    args = parser.parse_args()

    fetch_new = True
    if args.use_local:
        fetch_new = False

    genbank_mirror = args.genbank_mirror
    path_vars, assembly_summary, species = setup(genbank_mirror, args.species, fetch_new)
    info_dir, slurm, out, logger = path_vars
    genbank_status = assess_genbank(genbank_mirror, assembly_summary, species, logger)

    if args.update:
        update(genbank_mirror, genbank_status, path_vars, assembly_summary, species)

if __name__ == "__main__":
    main()
