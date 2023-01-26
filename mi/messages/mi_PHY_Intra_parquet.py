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

filename = glob.glob(mi_path+"*_Intra_*.pkl")  #
for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
    # df_detected = df.drop(columns=["Number of Neighbor Cells","Neighbor Cells_Physical Cell ID","Neighbor Cells_RSRP(dBm)","Neighbor Cells_RSRQ(dB)"])
    # df_neighbor = df.drop(columns=["Number of Detected Cells","Detected Cells_Physical Cell ID","Detected Cells_SSS Corr Value","Detected Cells_Reference Time"])
    
    # columns = [c for c in df_detected.columns if type(df_detected[c].iloc[0]) is list]
    # if columns :
    #   df_detected= df_detected.explode(columns, ignore_index=True)
    # columns = [c for c in df_neighbor.columns if type(df_neighbor[c].iloc[0]) is list]
    # if columns :
    #   df_neighbor= df_neighbor.explode(columns, ignore_index=True)
      
    # f = f.replace('/mnt/my_dataset/', '')
    # f2 = f.replace(meas, '')
    # df_detected.to_parquet(out_path+f2+"_Detected_Cell"+meas+".parquet", compression="gzip")
    # df_neighbor.to_parquet(out_path+f2+"_Neighbor_Cell"+meas+".parquet", compression="gzip")
    columns = ['RSRP(dBm)', 'RSRQ(dB)']  #, 'Physical Cell ID' , , ''
    df = df.explode(columns, ignore_index=True)
    df = df.explode('Physical Cell ID', ignore_index=True)
    df = df.explode('SSS Corr Value', ignore_index=True)
    df = df.explode('Reference Time', ignore_index=True)
    
    df.to_parquet(out_path+f+".parquet", compression="gzip")
    

print("Processing is done!")
