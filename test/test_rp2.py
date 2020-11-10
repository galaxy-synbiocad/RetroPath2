import unittest
import docker
import os
import json
import hashlib
import tempfile
import tarfile
import sys
import urllib.request
import shutil

sys.path.insert(0, '../galaxy/code/')

import tool_RetroPath2

class TestRP2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #### data ######
        cls.data_dir = tempfile.TemporaryDirectory()
        tar = tarfile.open('data.tar.xz', mode='r')
        tar.extractall(path=cls.data_dir.name)
        tar.close()
        #### docker ####
        cls.client = docker.from_env()
        cls.docker_obj = cls.client.containers.run('brsynth/retropath2-redis', ports={'8888/tcp': 8888}, detach=True, stderr=True) 

    @classmethod
    def tearDownClass(cls):
        if isinstance(cls.data_dir, tempfile.TemporaryDirectory):
            cls.data_dir.cleanup()
        cls.docker_obj.stop()
 
    def test_hydroxystyrene(self):
        path = os.path.join(self.data_dir.name, 'data', 'hydroxystyrene')
        with tempfile.TemporaryDirectory() as tmp_output_folder:
            tool_RetroPath2.retropathUpload(os.path.join(path, 'sinkfile.csv'),
                                            os.path.join(path, 'source.csv'),
                                            4,
                                            os.path.join(path, 'rules.tar'),
                                            'tar',
                                            os.path.join(tmp_output_folder, 'rp_pathways.csv'),
                                            topx=1000)
            with open(os.path.join(tmp_output_folder, 'rp_pathways.csv'), 'rb') as rppath:
                self.assertEqual(hashlib.md5(rppath.read()).hexdigest(), 'c09f59805bc1b857bf823e597f8c50d8')

    def test_phenol(self):
        path = os.path.join(self.data_dir.name, 'data', 'phenol')
        with tempfile.TemporaryDirectory() as tmp_output_folder:
            tool_RetroPath2.retropathUpload(os.path.join(path, 'sinkfile.csv'),
                                            os.path.join(path, 'source.csv'),
                                            3,
                                            os.path.join(path, 'rules.tar'),
                                            'tar',
                                            os.path.join(tmp_output_folder, 'rp_pathways.csv'),
                                            topx=1000)
            with open(os.path.join(tmp_output_folder, 'rp_pathways.csv'), 'rb') as rppath:
                self.assertEqual(hashlib.md5(rppath.read()).hexdigest(), 'd5f8fbae9268ff29e31c42856d3c59a0')

    def test_mesaconate(self):
        path = os.path.join(self.data_dir.name, 'data', 'mesaconate')
        with tempfile.TemporaryDirectory() as tmp_output_folder:
            tool_RetroPath2.retropathUpload(os.path.join(path, 'sinkfile.csv'),
                                            os.path.join(path, 'source.csv'),
                                            4,
                                            os.path.join(path, 'rules.tar'),
                                            'tar',
                                            os.path.join(tmp_output_folder, 'rp_pathways.csv'),
                                            topx=1000)
            with open(os.path.join(tmp_output_folder, 'rp_pathways.csv'), 'rb') as rppath:
                self.assertEqual(hashlib.md5(rppath.read()).hexdigest(), '7479b86d5f88f8d5b9f3242a07ce2aa5')

    def test_ectoine(self):
        path = os.path.join(self.data_dir.name, 'data', 'ectoine')
        with tempfile.TemporaryDirectory() as tmp_output_folder:
            tool_RetroPath2.retropathUpload(os.path.join(path, 'sinkfile.csv'),
                                            os.path.join(path, 'source.csv'),
                                            5,
                                            os.path.join(path, 'rules.tar'),
                                            'tar',
                                            os.path.join(tmp_output_folder, 'rp_pathways.csv'),
                                            topx=1000)
            with open(os.path.join(tmp_output_folder, 'rp_pathways.csv'), 'rb') as rppath:
                self.assertEqual(hashlib.md5(rppath.read()).hexdigest(), 'b3c53e9b745c0da1758d7a74245989bc')

    def test_coumarate(self):
        path = os.path.join(self.data_dir.name, 'data', 'coumarate')
        with tempfile.TemporaryDirectory() as tmp_output_folder:
            tool_RetroPath2.retropathUpload(os.path.join(path, 'sinkfile.csv'),
                                            os.path.join(path, 'source.csv'),
                                            3,
                                            os.path.join(path, 'rules.tar'),
                                            'tar',
                                            os.path.join(tmp_output_folder, 'rp_pathways.csv'),
                                            topx=1000)
            with open(os.path.join(tmp_output_folder, 'rp_pathways.csv'), 'rb') as rppath:
                self.assertEqual(hashlib.md5(rppath.read()).hexdigest(), '3cf549f61df364d15847215e99e4a1a5')

if __name__ == '__main__':
    unittest.main()
