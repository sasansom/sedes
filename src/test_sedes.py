import unittest

import hexameter.scan
import sedes

class TestAssign(unittest.TestCase):
    def test_assign(self):
        # Od. 1.1
        LINE = "ἄνδρα μοι ἔννεπε, μοῦσα, πολύτροπον, ὃς μάλα πολλὰ"
        scansion, = hexameter.scan.analyze_line_metrical(LINE)
        self.assertEqual(sedes.assign(scansion), (
            ("ἄνδρα", "1", "+-"),
            ("μοι", "2.5", "-"),
            ("ἔννεπε", "3", "+--"),
            ("μοῦσα", "5", "+-"),
            ("πολύτροπον", "6.5", "-+--"),
            ("ὃς", "9", "+"),
            ("μάλα", "10", "--"),
            ("πολλὰ", "11", "++"),
        ))
