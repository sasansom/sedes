import unittest

import common

class TestParse(unittest.TestCase):
    def test_parse_dist_cond_vars_spec(self):
        for spec, expected_dist_vars, expected_cond_vars in (
            ("", (), ()),
            ("/", (), ()),
            ("aaa", ("aaa",), ()),
            ("aaa/bbb", ("aaa",), ("bbb",)),
            ("aaa,bbb/ccc,ddd", ("aaa", "bbb"), ("ccc", "ddd")),
            ("aaa/", ("aaa",), ()),
            ("/aaa", (), ("aaa",)),
            # Backslash escapes.
            ("aaa\\,bbb/ccc", ("aaa,bbb",), ("ccc",)),
            ("aaa\\/bbb/ccc", ("aaa/bbb",), ("ccc",)),
            ("aaa\\\\bbb/ccc", ("aaa\\bbb",), ("ccc",)),
            ("aaa\\abbb/ccc", ("aaaabbb",), ("ccc",)),
        ):
            try:
                dist_vars, cond_vars = common.parse_dist_cond_vars_spec(spec)
            except ValueError as e:
                self.fail(spec)

        # Inputs that should raise an exception.
        for spec in (
            "\\",
            "aaa\\",
            "aaa/\\",
            "aaa/\\",
            "aaa/\\",
            "aaa,",
            "aaa,/",
            "aaa/,bbb",
            "aaa/bbb,",
            "aaa,/bbb",
            "aaa,,bbb",
            "aaa/bbb/ccc",
        ):
            with self.assertRaises(ValueError, msg = spec):
                common.parse_dist_cond_vars_spec(spec)
