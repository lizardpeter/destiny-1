#!/usr/bin/env python3
"""Summarize sampled ETW instruction pointers from an xperf -a dumper text trace.

Aggregates only CPU samples in the selected native decoder DLL, not idle or
other processes. Does not publish raw ETL files or any proprietary DLL bytes.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

SAMPLE = re.compile(r'^\s*SampledProfile,\s')
MAPPING = re.compile(r'^\s*(ImageLoad|ImageDCStart|ImageDCEnd|ImageUnLoad|ImageRundown),')

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--module",choices=("d1_oodle3.dll","oo2core_3_win64.dll"),required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    counts=collections.Counter()
    sample_rows=0
    image_events=[]
    excluded=0
    funcs=collections.Counter()
    with args.raw.open("r",errors="replace",encoding="utf-8-sig") as handle:
        for line in handle:
            s=line.strip()
            if SAMPLE.match(s):
                # SampledProfile, Timestamp, Process Name (PID), TID, PC, CPU,
                # ThreadStartImage!Function, Image!Function, Count, Type
                fields=[x.strip() for x in s.split(",")]
                if len(fields)<9: continue
                module=fields[7].split("!",1)[0].strip('" ').lower()
                if module!=args.module.lower() or "python" not in fields[2].lower():
                    excluded+=1
                    continue
                try:
                    ip=int(fields[4],16)
                    weight=int(fields[8])
                except (ValueError,IndexError):
                    continue
                counts[ip]+=weight
                funcs[fields[7]]+=weight
                sample_rows+=1
            elif args.module.lower() in s.lower() and (
                MAPPING.match(s) or s.startswith("Image") or
                s.startswith("I-") or s.startswith("P-")):
                if len(image_events)<25:
                    image_events.append(s[:500])
    total=sum(counts.values())
    if not total: raise RuntimeError("No CPU samples matched Python process and "+args.module)
    histogram=collections.Counter()
    for ip,w in counts.items(): histogram[ip//64*64]+=w
    report={
        "module":args.module,"total_weight":total,"individual_sample_records":sample_rows,
        "unique_instruction_addresses":len(counts),"other_samples_skipped":excluded,
        "top_instruction_pcs":[{"address":hex(ip),"weight":w,"fraction":round(w/total,6)}
                              for ip,w in counts.most_common(45)],
        "top_64_byte_buckets":[{"start_va":hex(ip),"weight":w,"fraction":round(w/total,6)}
                                for ip,w in histogram.most_common(35)],
        "symbolized_names":funcs.most_common(18),
        "image_load_candidates":image_events,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print("ETW_IP_SAMPLES",json.dumps({
        "module":args.module,"sample_rows":sample_rows,"weight":total,
        "unique_ips":len(counts),"top_64b_va":report["top_64_byte_buckets"][:14],
        "image_events":image_events[:8]},sort_keys=True))
if __name__=="__main__":
    main()
