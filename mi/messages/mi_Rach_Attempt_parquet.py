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



filename = glob.glob(mi_path+"*_Rach_*.pkl")  # PDCP,MAC, RRC , NAS done

for f in filename:
    f = f.replace('.pkl', '')
    print(f)
    df = pd.read_pickle(f+".pkl")
 
    if "Msg1" in df.columns:
        df1 = df.drop(columns=["Msg2","Msg3"])
        df2 = df.drop(columns=["Msg1","Msg3"])
        df3 = df.drop(columns=["Msg1","Msg2"])

        df1=df1[df1["Msg1"].isnull() != True]
        df1= df1.explode(["Msg1"], ignore_index=True)
        columns = [c for c in df1.columns if type(df1[c].iloc[0]) is list]
        df1= df1.explode(columns, ignore_index=True)
    #     df1 = df1[df1["Msg1"].isnull() != True]
        df1 = pd.concat([df1.drop(columns=["Msg1"]), pd.DataFrame(df1["Msg1"].apply(pd.Series))], axis='columns')

        df2=df2[df2["Msg2"].isnull() != True]
        df2= df2.explode("Msg2", ignore_index=True)
        columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]
        df2= df2.explode(columns, ignore_index=True)
    #     df2=df2[df2["Msg2"].isnull() != True]
        df2 = pd.concat([df2.drop(columns=["Msg2"]), pd.DataFrame(df2["Msg2"].apply(pd.Series))], axis='columns')
        columns = [c for c in df2.columns if type(df2[c].iloc[1]) is list]
        if columns: 
            df2= df2.explode(columns, ignore_index=True)
            df2 = pd.concat([df2.drop(columns=["MAC PDUs"]), pd.DataFrame(df2["MAC PDUs"].apply(pd.Series))], axis='columns') 
        columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]
        if columns: 
            df2=df2[df2["MAC PDUs"].isnull() != True]
            df2= df2.explode(columns, ignore_index=True)
            df2 = pd.concat([df2.drop(columns=["MAC PDUs"]), pd.DataFrame(df2["MAC PDUs"].apply(pd.Series))], axis='columns') 
        if 0 in df2.columns: 
            df2 = df2.drop(columns=[0])

        df3=df3[df3["Msg3"].isnull() != True]
        df3= df3.explode("Msg3", ignore_index=True)
        columns = [c for c in df3.columns if type(df3[c].iloc[0]) is list]
        df3= df3.explode(columns, ignore_index=True)
        df3 = pd.concat([df3.drop(columns=["Msg3"]), pd.DataFrame(df3["Msg3"].values.tolist())], axis='columns')  
        columns = [c for c in df3.columns if type(df3[c].iloc[0]) is list]
        if columns: 
            df3= df3.explode(columns, ignore_index=True)
            df3 = pd.concat([df3.drop(columns=["MAC PDUs"]), pd.DataFrame(df3["MAC PDUs"].apply(pd.Series))], axis='columns') 

        df1.to_parquet(out_path+f+"_Msg1.parquet", compression="gzip")
        df2.to_parquet(out_path+f+"_Msg2.parquet", compression="gzip")
        df3.to_parquet(out_path+f+"_Msg3.parquet", compression="gzip")

    else: 
    #     df1 = df.drop(columns=["Msg2","Msg3"])
        df2 = df.drop(columns=["Msg3"])
        df3 = df.drop(columns=["Msg2"])

    #     columns = [c for c in df1.columns if type(df1[c].iloc[0]) is list]
    #     df1= df1.explode(columns, ignore_index=True)
    #     df1 = df1[df1["Msg1"].isnull() != True]
    #     df1= df1.explode(["Msg1"], ignore_index=True)
    #     df1 = pd.concat([df1.drop(columns=["Msg1"]), pd.DataFrame(df1["Msg1"].values.tolist())], axis='columns')

        df2=df2[df2["Msg2"].isnull() != True]
        df2= df2.explode("Msg2", ignore_index=True)
        columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]
        df2= df2.explode(columns, ignore_index=True)
        df2 = pd.concat([df2.drop(columns=["Msg2"]), pd.DataFrame(df2["Msg2"].apply(pd.Series))], axis='columns')  
        columns = [c for c in df2.columns if type(df2[c].iloc[1]) is list]
        if columns: 
            df2= df2.explode(columns, ignore_index=True)
            df2 = pd.concat([df2.drop(columns=["MAC PDUs"]), pd.DataFrame(df2["MAC PDUs"].apply(pd.Series))], axis='columns') 
        columns = [c for c in df2.columns if type(df2[c].iloc[0]) is list]
        if columns: 
            df2=df2[df2["MAC PDUs"].isnull() != True]
            df2= df2.explode(columns, ignore_index=True)
            df2 = pd.concat([df2.drop(columns=["MAC PDUs"]), pd.DataFrame(df2["MAC PDUs"].apply(pd.Series))], axis='columns') 
        if 0 in df2.columns: 
            df2 = df2.drop(columns=[0])


        df3=df3[df3["Msg3"].isnull() != True]
        df3= df3.explode("Msg3", ignore_index=True)
        columns = [c for c in df3.columns if type(df3[c].iloc[0]) is list]
        df3= df3.explode(columns, ignore_index=True)
        df3 = pd.concat([df3.drop(columns=["Msg3"]), pd.DataFrame(df3["Msg3"].values.tolist())], axis='columns')  
        columns = [c for c in df3.columns if type(df3[c].iloc[0]) is list]
        if columns: 
            df3= df3.explode(columns, ignore_index=True)
            df3 = pd.concat([df3.drop(columns=["MAC PDUs"]), pd.DataFrame(df3["MAC PDUs"].apply(pd.Series))], axis='columns') 
    
        # df1.to_parquet(out_path+f+"_Msg1.parquet", compression="gzip")
        df2.to_parquet(out_path+f+"_Msg2.parquet", compression="gzip")
        df3.to_parquet(out_path+f+"_Msg3.parquet", compression="gzip")
        



print("Processing is done!")
