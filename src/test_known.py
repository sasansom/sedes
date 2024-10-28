import unittest

import known

class TestKnown(unittest.TestCase):
    def test_total_length(self):
        for line, scansion in known.KNOWN_SCANSIONS.items():
            length = sum(sum({"-": 0.5, "+": 1}[c] for c in metrical_shape) for word, metrical_shape in scansion)
            self.assertLessEqual(length, 12, (line, scansion))
