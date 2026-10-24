#!/usr/bin/env python3
"""Składa repozytorium APT dla Cydii ze wszystkich plików .deb w folderze.

Użycie:  python3 tools/build_repo.py <folder_z_deb> <folder_wyjsciowy> <adres_strony>

W folderze wyjściowym powstają: Packages, Packages.gz, Packages.bz2, Release, debs/*.deb
oraz pakiety.json (lista paczek dla strony głównej).
"""
import bz2, glob, gzip, hashlib, json, os, shutil, subprocess, sys


def control_of(deb):
    out = subprocess.run(["dpkg-deb", "-f", deb], check=True, capture_output=True).stdout
    return out.decode("utf-8").rstrip("\n")


def fields(ctrl):
    d = {}
    for line in ctrl.split("\n"):
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def digests(path):
    h = {k: hashlib.new(k) for k in ("md5", "sha1", "sha256")}
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            for v in h.values():
                v.update(chunk)
    return {k: v.hexdigest() for k, v in h.items()}


def main(src, out, site):
    if not site.endswith("/"):
        site += "/"
    debs = sorted(glob.glob(os.path.join(src, "*.deb")))
    os.makedirs(os.path.join(out, "debs"), exist_ok=True)
    blocks, listing = [], []
    for deb in debs:
        ctrl = control_of(deb)
        f = fields(ctrl)
        name = os.path.basename(deb)
        shutil.copy(deb, os.path.join(out, "debs", name))
        d = digests(deb)
        block = ctrl + "\n"
        block += "Filename: debs/%s\nSize: %d\nMD5sum: %s\nSHA1: %s\nSHA256: %s\n" % (
            name, os.path.getsize(deb), d["md5"], d["sha1"], d["sha256"])
        blocks.append(block)
        listing.append({"package": f.get("Package", ""), "name": f.get("Name", f.get("Package", "")),
                        "version": f.get("Version", ""), "description": f.get("Description", ""),
                        "section": f.get("Section", ""), "icon": f.get("Icon", ""),
                        "homepage": f.get("Depiction", f.get("Homepage", "")),
                        "size": os.path.getsize(deb)})
    packages = ("\n".join(blocks)).encode("utf-8")
    with open(os.path.join(out, "Packages"), "wb") as fh:
        fh.write(packages)
    with gzip.open(os.path.join(out, "Packages.gz"), "wb", 9) as fh:
        fh.write(packages)
    with open(os.path.join(out, "Packages.bz2"), "wb") as fh:
        fh.write(bz2.compress(packages, 9))
    with open(os.path.join(out, "Release"), "w", encoding="utf-8") as fh:
        fh.write("Origin: nazar0vsky\nLabel: nazar0vsky\nSuite: stable\nVersion: 1.0\nCodename: ios\n"
                 "Architectures: iphoneos-arm\nComponents: main\n"
                 "Description: Aplikacje i tweaki dla starszych iOS-ów (nazar0vsky-slam0)\n")
    with open(os.path.join(out, "pakiety.json"), "w", encoding="utf-8") as fh:
        json.dump({"repo": site, "packages": listing}, fh, ensure_ascii=False)
    print("Paczek w repozytorium: %d" % len(listing))
    for p in listing:
        print("  %s %s" % (p["package"], p["version"]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
