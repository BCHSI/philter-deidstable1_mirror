import unittest
import sys
import os
import filecmp

sys.path.append('./')
from src.philter.philter import Philter
# from src.philter.coordinate_map import CoordinateMap


class TestPhilter(unittest.TestCase):
    def remove_test_data(self):
        #the current code remove all files while keeping the directory.
        for f in os.listdir('./src/tests/test_result/'):
            os.remove('./src/tests/test_result/' + f)

    def test_blacklist(self):
        # Add testing code here
        # This is just an example:
        philter_config = {
            "verbose": False,
            "run_eval": False,
            "freq_table": False,
            "finpath": './src/tests/test_data/',
            "foutpath": './src/tests/test_result/',
            "outformat": "asterisk",
            "ucsfformat": False,
            "anno_folder": './src/tests/test_anno/',
            "filters": './src/tests/test_config/philter_alpha.json',
            "xml": './src/tests/phi_notes.json',
            "coords": './src/tests/coordinates.json',
            "stanford_ner_tagger": {
                "classifier": '/usr/local/stanford-ner/' + "classifiers/english.all.3class.distsim.crf.ser.gz",
                "jar": '/usr/local/stanford-ner/' + "stanford-ner.jar",
                "download": True,
            }
        }


        #TODO: call the scrip
        #test_filterer = Philter(philter_config)
        #test_filterer.map_coordinates(philter_config["finpath"])
        #test_filterer.transform(in_path=philter_config["finpath"],
        #                        out_path=philter_config["foutpath"],
        #                        replacement="*")
        res = filecmp.cmp(philter_config["foutpath"] + '110-01.txt', philter_config["anno_folder"] + '110-01.txt')
        self.assertIs(res, True)
        # self.remove_test_data()

    # def test_whitelist(self):
    #     Add testing code here
    #     self.assertEqual('foo'.upper(), 'FOO')
    #
    # def test_regex(self):
    #     Add testing code here
    #     self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhilter)
    unittest.TextTestRunner(verbosity=2).run(suite)
