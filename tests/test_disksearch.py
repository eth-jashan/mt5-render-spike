import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))
from disksearch import find_secret

class DiskSearchTest(unittest.TestCase):
    def test_find_secret_utf8(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "config"))
            with open(os.path.join(d, "config", "a.ini"), "wb") as f:
                f.write(b"Password=Inv@1\r\n")
            self.assertEqual(find_secret(d, "Inv@1"), [os.path.join("config", "a.ini")])

    def test_find_secret_utf16(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "accounts.dat"), "wb") as f:
                f.write("xxInv@1yy".encode("utf-16le"))
            self.assertEqual(find_secret(d, "Inv@1"), ["accounts.dat"])

    def test_find_secret_none(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.bin"), "wb") as f:
                f.write(b"nothing here")
            self.assertEqual(find_secret(d, "Inv@1"), [])

if __name__ == "__main__":
    unittest.main()
