#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import pandas as pd

def read_metaphlan_table(path: Path, sample_name: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", comment="#", header=0)
    if "clade_name" in df.columns and "relative_abundance" in df.columns:
        s = df.set_index("clade_name")["relative_abundance"]
    else:
        if df.shape[1] < 2:
            raise ValueError(f"{path} does not look like a MetaPhlAn table")
        s = df.iloc[:, -1]
        s.index = df.iloc[:, 0]
    s = pd.to_numeric(s, errors="coerce").fillna(0.0)
    s.name = sample_name
    return s.to_frame()

def infer_sample_name(f: Path) -> str:
    return f.name.replace("_metaphlan_profile.tsv", "") if f.name.endswith("_metaphlan_profile.tsv") else f.stem

def collapse_by_rank(df: pd.DataFrame, rank: str) -> pd.DataFrame:
    collapsed = df.groupby(lambda x: next((p for p in x.split("|") if p.startswith(rank + "__")), "unclassified")).sum()
    return collapsed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="MetaPhlAn input tables")
    parser.add_argument("merged_out", help="Merged output TSV")
    parser.add_argument("summary_out", help="Summary output TSV")
    parser.add_argument("--samples", nargs="+", help="Sample order", required=False)
    args = parser.parse_args()

    input_paths = [Path(p) for p in args.inputs]
    merged_out, summary_out = Path(args.merged_out), Path(args.summary_out)

    merged_df = None
    for f in input_paths:
        sample = infer_sample_name(f)
        df = read_metaphlan_table(f, sample)
        merged_df = df if merged_df is None else merged_df.join(df, how="outer")

    merged_df = merged_df.fillna(0.0)

    # Reorder columns by --samples if provided
    if args.samples:
        merged_df = merged_df.reindex(args.samples, axis=1)
    else:
        merged_df = merged_df.reindex(sorted(merged_df.columns), axis=1)

    merged_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(merged_out, sep="\t")

    # Per-rank summaries
    ranks = ["k", "p", "c", "o", "f", "g", "s"]
    summary_frames = []
    for r in ranks:
        collapsed = collapse_by_rank(merged_df, r).T
        collapsed = collapsed.reset_index().melt(id_vars="index", var_name="taxon", value_name="relative_abundance")
        collapsed = collapsed.rename(columns={"index": "sample_id"})
        collapsed["rank"] = r
        summary_frames.append(collapsed)

    summary_df = pd.concat(summary_frames, ignore_index=True)
    summary_df.to_csv(summary_out, sep="\t", index=False)

if __name__ == "__main__":
    main()
