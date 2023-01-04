#!/usr/bin/env python

import pandas as pd
from pathlib import Path
from pyarrow.lib import ArrowInvalid, ArrowTypeError

# ADAPT PATHS IF NEEDED
data_path = Path("/mnt/ai4mobile/datacloud")
berlin_path = data_path/"berlin_preprocessed"
in_path = berlin_path/"mi2log_parquet"
out_path = berlin_path/"mi_merged"


def merge(pc, msg):

    df_list = []
    for p in in_path.rglob(f"*/{pc}/*/*{msg}*.parquet"):
        print(p.relative_to(in_path))

        monitor = p.parent.stem
        df = pd.read_parquet(p)

        if df.index.dtype != 'datetime64[ns, Europe/Berlin]':
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            df.index = df.index.tz_localize("Europe/Berlin")
        df["file"] = monitor

        df_list.append(df)

    if len(df_list) == 0:
        print(f"No data found for {pc}, {msg}. Skipping...")
        return

    merge_df = pd.concat(df_list).sort_index()
    merge_cols = merge_df.columns
    print(f"Resulting dataframe length:{len(merge_df)}")
    print(f"Resulting {len(merge_cols)} columns:")
    for c in merge_cols:
        print(f"\t- {c}")

    save_dir = out_path/pc.replace("_", "")
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir/f"{msg}.parquet"
    try:
        merge_df.to_parquet(save_path, compression='gzip')
        print(f'Data saved as {save_path}')
    except (ArrowInvalid, ArrowTypeError) as ai:
        print(f"{save_path} cannot be saved as parquet. The following exception occurred:")
        print(ai)


def get_arg_list(root):
    root = Path(root)
    files = [f.relative_to(root) for f in root.rglob("*.parquet")]

    # Extract devices and msg types from path list
    msg_types = sorted(set(f.stem for f in files))
    devices = sorted(set(f.parent.parent.stem for f in files))

    return [{'device': d, 'msg': m} for d in devices for m in msg_types]


if __name__ == '__main__':

    import argparse

    arg_list = get_arg_list(in_path)

    parser = argparse.ArgumentParser(description='Merge MI parquet files for a single device.')

    parser.add_argument("--job-index", "-i", type=int,
                        help=f"Index to get args from 0 to {len(arg_list)-1}. Leave blank to loop through")
    args = parser.parse_args()

    job_i = args.job_index
    if job_i is not None:   # Select single job
        arg_list = [arg_list[job_i]]
    for a in arg_list:
        print(a)
        merge(pc=a['device'], msg=a['msg'])
