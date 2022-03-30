from ProcessImage import *
import unittest

class TestProcessImage(unittest.TestCase):
    def test_process(self):
        pro = ProcessImage("./Data/941b_x63_zoom08_1.tif")
        pro.process()

    def test_evaluate(self):
        pro = ProcessImage("./Data/751b_x63_zoom08_1.tif")
        pro.process()
        pro.evaluate('FN')


    def test_extract(self):
        pro = ProcessImage("./Data/113_x63_zoom08_1.tif")
        pro.process()
        pro.extract()

    def test_calculateFeatures(self):
        pro = ProcessImage("./Data/851b_x63_zoom08_1.tif")
        pro.process()
        pro.extract()
        pro.calculateFeatures()

    def test_export(self):
        pro = ProcessImage("./Data/113_x63_zoom08_1.tif")
        pro.process()
        pro.extract()
        pro.calculateFeatures()
        pro.export('.Result.csv')

if __name__ == '__main__':
    unittest.main()
