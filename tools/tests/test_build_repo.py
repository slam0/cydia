import bz2, gzip, json, os, subprocess, sys, tempfile, unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build_repo.py")


def make_deb(folder, pkg, version, extra=""):
    root = os.path.join(folder, "w_" + pkg)
    os.makedirs(os.path.join(root, "DEBIAN"), exist_ok=True)
    with open(os.path.join(root, "DEBIAN", "control"), "w", encoding="utf-8") as f:
        f.write("Package: %s\nName: Nazwa %s\nVersion: %s\nArchitecture: iphoneos-arm\nDescription: opis\n"
                "Maintainer: t\nSection: Utilities\n%s" % (pkg, pkg, version, extra))
    os.makedirs(os.path.join(folder, "src"), exist_ok=True)
    deb = os.path.join(folder, "src", "%s_%s.deb" % (pkg, version))
    subprocess.run(["dpkg-deb", "-b", root, deb], check=True, capture_output=True)


class T(unittest.TestCase):
    def test_two_packages(self):
        with tempfile.TemporaryDirectory() as d:
            make_deb(d, "com.a.one", "1.0", "Icon: https://x/i.png\nDepiction: https://x/\n")
            make_deb(d, "com.a.two", "2.5")
            out = os.path.join(d, "out")
            subprocess.run([sys.executable, SCRIPT, os.path.join(d, "src"), out, "https://x.github.io/cydia"], check=True)
            pk = open(os.path.join(out, "Packages"), encoding="utf-8").read()
            self.assertEqual(pk.count("Package: "), 2)
            self.assertIn("Filename: debs/com.a.two_2.5.deb", pk)
            self.assertEqual(gzip.open(os.path.join(out, "Packages.gz")).read().decode(), pk)
            self.assertEqual(bz2.open(os.path.join(out, "Packages.bz2")).read().decode(), pk)
            info = json.load(open(os.path.join(out, "pakiety.json"), encoding="utf-8"))
            self.assertEqual(len(info["packages"]), 2)
            self.assertEqual(info["packages"][0]["homepage"], "https://x/")
            self.assertEqual(info["repo"], "https://x.github.io/cydia/")
            self.assertIn("Architectures: iphoneos-arm", open(os.path.join(out, "Release")).read())

    def test_empty(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "src"))
            out = os.path.join(d, "out")
            subprocess.run([sys.executable, SCRIPT, os.path.join(d, "src"), out, "https://x/"], check=True)
            self.assertEqual(json.load(open(os.path.join(out, "pakiety.json")))["packages"], [])


if __name__ == "__main__":
    unittest.main()
