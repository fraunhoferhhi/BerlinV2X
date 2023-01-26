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
filename = glob.glob(mi_path+"*_PDCP_*.pkl")  # PDCP

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
    
    columns = [c for c in df.columns if type(df[c].iloc[0]) is list]
    df= df.explode(columns, ignore_index=True)
    df= df.explode("Released RBs", ignore_index=True)

    df = df[df["Number of active RBs"] != 0]   # column in PDCP files 


    df1 = df.drop(columns=["Added/Modified RBs"])
    df2 = df.drop(columns=["Active RBs"])

    df1= df1.explode("Active RBs", ignore_index=True)
    df2= df2.explode("Added/Modified RBs", ignore_index=True)

    df2 = df2[df2["Added/Modified RBs"].isnull() != True]


    df1 = pd.concat([df1.drop(columns=["Active RBs"]), pd.DataFrame(df1["Active RBs"].values.tolist())], axis='columns')
    df2 = pd.concat([df2.drop(columns=["Added/Modified RBs"]), pd.DataFrame(df2["Added/Modified RBs"].apply(pd.Series))], axis='columns')
    # df2 = df2[df2["timestamp"].isnull() != True]

    f = f.replace('/mnt/my_dataset/', '')
    f2 = f.replace(meas, '')
    df1.to_parquet(out_path+f2+"_Active_RBs"+meas+".parquet", compression="gzip")
    df2.to_parquet(out_path+f2+"_Added_Modified_RBs"+meas+".parquet", compression="gzip")


print("Processing is done!")
