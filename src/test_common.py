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

class TestRoundtrip(unittest.TestCase):
    def test_roundtrip(self):
        for dist_vars, cond_vars in (
            ((), ()),
            (("aaa",), ()),
            ((), ("aaa",)),
            (("aaa",), ("bbb",)),
            (("aaa", "bbb"), ("ccc", "ddd")),
            (("a/a,a\\a",), ()),
        ):
            spec = common.format_dist_cond_vars_spec(dist_vars, cond_vars)
            try:
                dist_vars_roundtrip, cond_vars_roundtrip = common.parse_dist_cond_vars_spec(spec)
            except ValueError as e:
                self.fail((dist_vars, cond_vars, spec))
            self.assertEqual((dist_vars, cond_vars), (dist_vars_roundtrip, cond_vars_roundtrip), spec)
