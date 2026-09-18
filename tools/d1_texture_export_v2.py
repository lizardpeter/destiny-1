#!/usr/bin/env python3
"""Fail-closed D1 PS4 texture exporter.

This is the production strict-chain entry point over d1_texture_export.py.  It
keeps the established byte/format export implementation but replaces the
legacy adjacency-based backing traversal with the source-closed resolver from
d1_texture_backing_chain_v1 before any export is attempted.

No semantic name is assigned to 65:1 or 5:1 here.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_texture_export as legacy
from d1_texture_backing_chain_v1 import resolve_texture_backing


def strict_follow_backing(global_by, header_entry):
    """Legacy-compatible adapter backed only by proven chain shapes."""
    first, backing, _mode = resolve_texture_backing(global_by, header_entry)
    return first, backing


def install_strict_chain_gate():
    """Install the gate used by legacy.export_reader's global lookup."""
    legacy.follow_backing = strict_follow_backing


def export_reader(*args, **kwargs):
    install_strict_chain_gate()
    return legacy.export_reader(*args, **kwargs)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--dependency-pkg',type=Path,action='append',default=[])
    ap.add_argument('--tag-hash',action='append')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    r=legacy.EntryReader(a.pkg,a.runtime)
    deps=[legacy.EntryReader(p,a.runtime) for p in a.dependency_pkg]
    rep=export_reader(r,a.out,tag_hashes=a.tag_hash,dependencies=deps)
    print(json.dumps({'package':rep['package'],
                      'logical_package_family':rep['logical_package_family'],
                      'dependencies':rep['dependency_packages'],
                      'texture_count':rep['texture_count'],
                      'missing_requested':rep['missing_requested']},indent=2))


if __name__=='__main__':
    main()
