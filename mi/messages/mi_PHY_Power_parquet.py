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


filename = glob.glob(mi_path+"*_PUCCH_*.pkl")  # PHY_PUCCH_Power_Control ,PHY_PUSCH_Power_Control

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
    
    columns = [c for c in df.columns if type(df[c].iloc[0]) is list]
    df= df.explode(columns, ignore_index=True)
    
    df['TPC Command'] = df['TPC Command'].astype(str) #PHY_PUCCH_Power_Control, requirs only 1 time explode
    # df['TPC'] = df['TPC'].astype(str) #PPHY_PUSCH_Power_Control, requirs only 1 time explode

    
    f = f.replace('/mnt/my_dataset/', '')
    df.to_parquet(out_path+f+".parquet", compression="gzip")


print("Processing is done!")
