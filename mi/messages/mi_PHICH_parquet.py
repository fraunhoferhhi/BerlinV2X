import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np
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
filename = glob.glob(mi_path+"*_PHICH_*.pkl")  # PHICH

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

    df['PHICH Value'] = df['PHICH Value'].astype(str)  # column in PHICH  file

    df2 = df[df["PDCCH Info"].isnull() != True]
    df = df.drop(columns=["PDCCH Info"])

    # df2 = pd.concat([df2.drop(columns=["PDCCH Info"]), pd.DataFrame(df2["PDCCH Info"].values.tolist())], axis='columns')  
    df2 = pd.concat([df2.drop(columns=["PDCCH Info"]), pd.DataFrame(df2["PDCCH Info"].apply(pd.Series))], axis='columns') 
    # df2 = df2[df2["timestamp"].isnull() != True ]

    f = f.replace('/mnt/my_dataset/', '')
    f2 = f.replace(meas, '')
    df.to_parquet(out_path+f+".parquet", compression="gzip")
    df2.to_parquet(out_path+f2+"_PDCCH_Info"+meas+".parquet", compression="gzip")



print("Processing is done!")
