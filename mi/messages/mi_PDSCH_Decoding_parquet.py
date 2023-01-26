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


filename = glob.glob(mi_path+"*PDSCH_Decoding_*.pkl")  # decoding 

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
        columns = [i for i in df.columns if isinstance(df[i][0],dict)]  # check if there are dicts in columns 
        if columns :
            df = df[df["Streams"].isnull() != True]
            df = pd.concat([df.drop(columns=columns)] + [pd.DataFrame(df[c].apply(pd.Series)) for c in columns] , axis='columns')
            
            df= df.explode(["Energy Metrics"], ignore_index=True)
            df = df[df["Energy Metrics"].isnull() != True]
            df= pd.concat([df.drop(columns=["Energy Metrics"]), pd.DataFrame(df["Energy Metrics"].apply(pd.Series))], axis='columns')  

    f = f.replace('/mnt/my_dataset/', '')
    df.to_parquet(out_path+f+".parquet", compression="gzip")


print("Processing is done!")
