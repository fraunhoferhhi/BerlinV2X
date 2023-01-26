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


filename = glob.glob(mi_path+"*_PHY_Idle_*.pkl")  # LTE_PHY_Idle

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")

    columns = [ 'Num Rx Ant', 'Serving Cell Index']
    df = df.explode(columns, ignore_index=True)
    df = df.explode("Version", ignore_index=True)
    columns = [ 'SubPacket ID', 'SubPacket Size', 'E-ARFCN', 'Num Cells', 'Deplexing Mode']
    df = df.explode(columns, ignore_index=True)
    df = df.explode("Neighbor Cells", ignore_index=True)
    df = df.explode("Neighbor Cells", ignore_index=True)
    df= pd.concat([df.drop(columns=["Neighbor Cells"]), pd.DataFrame(df["Neighbor Cells"].values.tolist())], axis='columns')  



    
    f = f.replace('/mnt/my_dataset/', '')
    df.to_parquet(out_path+f+".parquet", compression="gzip")


print("Processing is done!")
