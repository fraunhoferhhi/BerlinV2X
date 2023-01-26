import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
import os
import glob
import argparse
import pickle

pwd = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", type=str, help="Input file")
parser.add_argument("--outfile", "-o", type=str, help="Output file")
args = parser.parse_args()
mi_path= args.input
out_path= args.outfile

meas = "-15"

filename = glob.glob(mi_path+"*_PHY_*.pkl")  # all the files

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
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

    df['SN'] = df['SN'].astype(str)
    
    if "RLC DATA LI" in df.columns:
        df2 = df[df["RLC DATA LI"].isnull() != True ]
        df  = df.drop(columns=["RLC DATA LI"])
        columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]    
        if columns:
            print(f"Columns to explode: {columns}")
            df2 = df2.explode(columns, ignore_index=True)
            df2 = pd.concat([df2.drop(columns=columns)] +
                    [pd.DataFrame(df2[c].values.tolist()) for c in columns], axis='columns')
                
    f = f.replace('/mnt/my_dataset/', '')
    f2 = f.replace(meas, '')

    df.to_parquet(out_path+f+".parquet", compression="gzip")
    df2.to_parquet(out_path+f2+"_Data_LI"+meas+".parquet", compression="gzip")


print("Processing is done!")
