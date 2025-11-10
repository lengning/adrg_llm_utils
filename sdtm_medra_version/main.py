#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd

# Common IG → Model mapping (extend if your study uses others)
SDTM_IG_TO_MODEL = {
    "3.1.1": "1.1",
    "3.1.2": "1.2",
    "3.1.3": "1.3",
    "3.2": "1.4",
    "3.3": "1.7",
    "3.4": "2.0",
    "3.5": "2.1",
}

def extract_from_define(define_xml: Path):
    tree = ET.parse(str(define_xml))
    root = tree.getroot()

    # Find MetaDataVersion regardless of namespace
    mdv = None
    for el in root.iter():
        if el.tag.endswith("MetaDataVersion"):
            mdv = el
            break
    if mdv is None:
        raise RuntimeError("MetaDataVersion not found in define.xml")

    # Grab attributes by local name (namespace-agnostic)
    attrs = {k.split("}")[-1]: v for k, v in mdv.attrib.items()}
    sdtm_ig = (attrs.get("StandardVersion") or "").strip()
    sdtm_model = SDTM_IG_TO_MODEL.get(sdtm_ig, "")
    define_version = (attrs.get("DefineVersion") or "").strip()

    # Best-effort MedDRA version sniff: prefer XML attributes over brittle regex
    meddra = ""
    # Search for an element that has Dictionary="MEDDRA" (case-insensitive)
    for el in root.iter():
        dict_val = el.attrib.get("Dictionary") or el.attrib.get("dictionary") or ""
        if dict_val.upper() == "MEDDRA":
            # Version attribute may be 'Version' or 'version'
            v = el.attrib.get("Version") or el.attrib.get("version")
            if v:
                meddra = v
                break

    # Fallback: try to catch textual occurrences with a broader regex (optional)
    if not meddra:
        m = re.search(
            r'Dictionary\s*=\s*["\']MEDDRA["\'][^>]*Version\s*=\s*["\']([0-9]+(?:\.[0-9]+)*)["\']',
            define_xml.read_text(encoding="utf-8", errors="ignore"),
            re.IGNORECASE,
        )
        if m:
            meddra = m.group(1)
        else:
            # older fallback (keeps original behaviour)
            m2 = re.search(r"MedDRA\s*(?:version|v)?\s*([0-9]+(?:\.[0-9]+)*)", define_xml.read_text(encoding="utf-8", errors="ignore"), re.IGNORECASE)
            if m2:
                meddra = m2.group(1)

    return sdtm_ig, sdtm_model, meddra, define_version

def main():
    ap = argparse.ArgumentParser(
        description="Extract SDTM IG Version, SDTM Version, MedDRA version, and Define version from define.xml and write a CSV."
    )
    ap.add_argument("--define", required=True, type=Path, help="Path to define.xml")
    ap.add_argument("--out", type=Path, default=Path("standards_from_define.csv"),
                    help="Output CSV file (default: standards_from_define.csv)")
    args = ap.parse_args()

    sdtm_ig, sdtm_model, meddra, define_version = extract_from_define(args.define)

    rows = []
    sdtm_bits = []
    if sdtm_ig:
        sdtm_bits.append(f"SDTM Implementation Guide Version {sdtm_ig}")
    if sdtm_model:
        sdtm_bits.append(f"SDTM Version {sdtm_model}")
    rows.append(["SDTM", " ; ".join(sdtm_bits)])
    rows.append(["Medical Events Dictionary", f"MedDRA version {meddra}" if meddra else ""])
    rows.append(["Define-XML", f"Define version {define_version}" if define_version else ""])

    pd.DataFrame(rows, columns=["Standard or Dictionary", "Versions Used"]).to_csv(args.out, index=False)

if __name__ == "__main__":
    main()