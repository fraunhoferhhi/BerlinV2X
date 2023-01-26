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
filename = glob.glob(mi_path+"*_MAC_Conf*.pkl")  #

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
    f = f.replace('/mnt/my_dataset/', '')
    f2 = f.replace(meas, '')
    columns = [
    'Config reason',
    'TA Timer',
    'SR periodicity',
    'BSR timer',
    'SPS Number of Tx released',
    'Retx BSR timer',
    'Preamble initial power',
    'Power ramping step',
    'RA index1',
    'RA index2',
    'Preamble trans max',
    'Contention resolution timer',
    'Message size Group_A',
    'Power offset Group_B',
    'PMax',
    'Delta preamble Msg3',
    'PRACH config',
    'CS zone length',
    'Root seq index',
    'PRACH Freq Offset',
    'High speed flag',
    'Max retx Msg3',
    'RA rsp win size',
    'Number of deleted LC',
    'Number of added/modified LC']
    df= df.explode(columns, ignore_index=True)
    df= df.explode(["Num eMBMS Active LCs"], ignore_index=True)
    cols = ['SubPacket ID','SubPacket Size']
    df= df.explode(cols, ignore_index=True)
    df= df.explode(["Version"], ignore_index=True)

if 'added/modified LC' in df.columns: 
    df= df.explode(["added/modified LC"], ignore_index=True)
    df1= df[df['added/modified LC'] == 0]
    df2 = df[df['added/modified LC'] != 0]
    df2 = pd.concat([df2.drop(columns=["added/modified LC"]), pd.DataFrame(df2["added/modified LC"].apply(pd.Series))], axis='columns')
    df1.to_parquet(out_path+f+".parquet", compression="gzip")
    df2.to_parquet(out_path+f2+"_Added_Modified_LC"+meas+".parquet", compression="gzip")
    
else:
  df.to_parquet(out_path+f+".parquet", compression="gzip") 
    # cc = [ 'log_msg_len', 'type_id', 'timestamp', 'Version', 'Num SubPkt','Subpackets_added/modified LC']

    # if 'Subpackets_added/modified LC' in df.columns:
    #   df1 = df.drop(columns=['Subpackets_added/modified LC'])
    #   df2= df[cc]
    #   columns = [c for c in df1.columns if type(df1[c].iloc[0]) is list]
    #   df1= df1.explode(columns, ignore_index=True)
    #   df1.to_parquet(out_path+f+".parquet", compression="gzip")
      
    #   columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]
    #   if columns:
    #     df2= df2.explode(columns, ignore_index=True)
    #     df2 = df2[df2["Subpackets_added/modified LC"].isnull() != True]
    #     df2 = pd.concat([df2.drop(columns=["Subpackets_added/modified LC"]), pd.DataFrame(df2["Subpackets_added/modified LC"].values.tolist())], axis='columns') 
    #     df2 = df2[df2["timestamp"].isnull() != True]
    #     df2.to_parquet(out_path+f2+"_Added_Modified_LC"+meas+".parquet", compression="gzip")
    # else:
    #   columns = [c for c in df.columns if type(df[c].iloc[0]) is list]
    #   df= df.explode(columns, ignore_index=True)
    #   df.to_parquet(out_path+f+".parquet", compression="gzip") 

  
  
 


print("Processing is done!")
