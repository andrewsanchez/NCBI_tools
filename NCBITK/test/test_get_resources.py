from NCBITK import config
from NCBITK import get_resources

import unittest
import os
import glob
import tempfile
import shutil
import pandas as pd


class TestGetResources(unittest.TestCase):
    def setUp(self):
        self.genbank_mirror = tempfile.mkdtemp(prefix='Genbank_')
        self.path_vars = config.instantiate_path_vars(self.genbank_mirror)
        self.info_dir, self.slurm, self.out, self.logger = self.path_vars
        self.assembly_summary = get_resources.get_assembly_summary(self.genbank_mirror, True)
        self.assertIsInstance(self.assembly_summary, pd.DataFrame)

    def test_get_scientific_names(self):
        names = get_resources.get_scientific_names(self.genbank_mirror, self.assembly_summary)
        self.assertIsInstance(names, pd.DataFrame)

    def test_update_assembly_summary(self):
        names = get_resources.get_scientific_names(self.genbank_mirror, self.assembly_summary)
        updated_assembly_summary = get_resources.update_assembly_summary(self.genbank_mirror, self.assembly_summary, names)
        self.assertIsInstance(updated_assembly_summary, pd.DataFrame)

    def test_clean_up_assembly_summary(self):
        clean_assembly_summary = get_resources.clean_up_assembly_summary(
            self.genbank_mirror,
            self.local_assembly_summary)
        self.assertTrue(os.path.isfile(self.path_assembly_summary))
        self.assertIsInstance(clean_assembly_summary, pd.DataFrame)

    def tearDown(self):
        shutil.rmtree(self.genbank_mirror)


if __name__ == '__main__':
    unittest.main()
