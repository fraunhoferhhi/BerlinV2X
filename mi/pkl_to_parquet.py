#!/usr/bin/python

import pandas as pd
from pathlib import Path
from pyarrow.lib import ArrowInvalid, ArrowTypeError

# ADAPT PATHS IF NEEDED
mount_datacloud = Path('/mnt/ai4mobile/datacloud')
in_root = mount_datacloud/"berlin_preprocessed/mi2log_pkl"
out_root = mount_datacloud/"berlin_preprocessed/mi2log_parquet"

# Read file list from base directory
files = sorted([str(f.relative_to(in_root)) for f in in_root.rglob("*.pkl")])


def main(file=None):

    if file is None:
        file_list = files
    else:
        file_list = [file]

    for file in file_list:

        out_path = Path(out_root/file).with_suffix(".parquet")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f'reading file {file}')
        df = pd.read_pickle(in_root/file)
        ### TODO START OF BORROWED BLOCK FROM KHAWLA ###
        columns = [c for c in df.columns if type(df[c].iloc[0]) is list]
        if columns:
            print(f"Columns to explode: {columns}")
            df = df.explode(columns, ignore_index=True)
        columns = [c for c in df.columns if type(df[c].iloc[0]) is list]
        if columns:
            print(f"Columns to explode: {columns}")
            df = df.explode(columns, ignore_index=True)
            df = pd.concat([df.drop(columns=columns)] +
                           [pd.DataFrame(df[c].values.tolist()) for c in columns], axis='columns')
        try:
            df = rename_duplicated_columns(df)
            df.to_parquet(out_path, compression="gzip")
            print(f"Saved as {out_path}")
        ### TODO END OF BORROWED BLOCK FROM KHAWLA ###
        except (ArrowInvalid, ArrowTypeError) as ai:
            print(f"{out_path.stem} cannot be saved as parquet. The following exception occurred:")
            print(ai)


def rename_duplicated_columns(df):
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' +
                                                         str(i) if i != 0 else dup
                                                         for i in range(sum(cols == dup))]
    df.columns = cols

    return df


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file-index", "-i", type=int, help="Index of job according to presaved list, from 0 to "
                                                             f"{len(files)-1}. "
                                                             f"Leave blank to loop through.")

    args = parser.parse_args()

    index = args.file_index
    f_input = None if index is None else files[index]
    main(file=f_input)
