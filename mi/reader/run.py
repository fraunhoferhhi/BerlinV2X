#!/usr/bin/python
#This is the file for starting the parser. Here you start the MI analyzer, define editing and saving of the data and which data you'd like to collect

import numpy as np
import configparser
import pandas as pd
from parser_mi_simple import MiAnalyzer #local file
# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
import logging
import gc
from pathlib import Path
"""
Offline analysis by replaying logs
"""

mount_datacloud = Path('/mnt/ai4mobile/datacloud')
in_root = mount_datacloud/"berlin"
out_root = mount_datacloud/"berlin_preprocessed/mi2log_pkl"

# Use default_config if no cfg file is given or entries are missing from the cfg file.
default_config = {
    "logging": {
        "log_file_path": str(in_root),
    },
    "modem_info" : {
        "device_path" : "/dev/ttyUSB0",
        "baud_rate" : 115200,
    }
}

# Read file list from base directory
files = sorted([str(f.relative_to(in_root)) for f in in_root.rglob("*.mi2log")])

msg_list = ['LTE_MAC_Configuration',
            'LTE_MAC_DL_Transport_Block',
            'LTE_MAC_Rach_Attempt',
            'LTE_MAC_Rach_Trigger',
            'LTE_MAC_UL_Buffer_Status_Internal',
            'LTE_MAC_UL_Transport_Block',
            'LTE_MAC_UL_Tx_Statistics',
            'LTE_NAS_EMM_OTA_Incoming_Packet',
            'LTE_NAS_EMM_OTA_Outgoing_Packet',
            'LTE_NAS_EMM_State',
            'LTE_NAS_ESM_OTA_Incoming_Packet',
            'LTE_NAS_ESM_OTA_Outgoing_Packet',
            'LTE_NAS_ESM_State',
            'LTE_PDCP_DL_Cipher_Data_PDU',
            'LTE_PDCP_DL_Config',
            'LTE_PDCP_DL_Ctrl_PDU',
            'LTE_PDCP_DL_SRB_Integrity_Data_PDU',
            'LTE_PDCP_DL_Stats',
            'LTE_PDCP_UL_Cipher_Data_PDU',
            'LTE_PDCP_UL_Config',
            'LTE_PDCP_UL_Ctrl_PDU',
            'LTE_PDCP_UL_SRB_Integrity_Data_PDU',
            'LTE_PDCP_UL_Stats',
            'LTE_PHY_BPLMN_Cell_Confirm',
            'LTE_PHY_BPLMN_Cell_Request',
            'LTE_PHY_Connected_Mode_Intra_Freq_Meas',
            'LTE_PHY_Connected_Mode_Neighbor_Measurement',
            'LTE_PHY_Idle_Neighbor_Cell_Meas',
            'LTE_PHY_Inter_Freq_Log',
            'LTE_PHY_Inter_RAT_Measurement',
            'LTE_PHY_PDCCH_Decoding_Result',
            'LTE_PHY_PDCCH_PHICH_Indication_Report',
            'LTE_PHY_PDSCH_Decoding_Result',
            'LTE_PHY_PDSCH_Packet',
            'LTE_PHY_PDSCH_Stat_Indication',
            'LTE_PHY_PUCCH_CSF',
            'LTE_PHY_PUCCH_Power_Control',
            'LTE_PHY_PUCCH_Tx_Report',
            'LTE_PHY_PUSCH_CSF',
            'LTE_PHY_PUSCH_Power_Control',
            'LTE_PHY_PUSCH_Tx_Report',
            'LTE_PHY_RLM_Report',
            'LTE_PHY_Serv_Cell_Measurement',
            'LTE_PHY_Serving_Cell_COM_Loop',
            'LTE_PHY_System_Scan_Results',
            'LTE_RLC_DL_AM_All_PDU',
            'LTE_RLC_DL_Config_Log_Packet',
            'LTE_RLC_DL_Stats',
            'LTE_RLC_UL_AM_All_PDU',
            'LTE_RLC_UL_Config_Log_Packet',
            'LTE_RLC_UL_Stats',
            'LTE_RRC_CDRX_Events_Info',
            'LTE_RRC_MIB_Packet',
            'LTE_RRC_OTA_Packet',
            'LTE_RRC_Serv_Cell_Info',
            'Modem_debug_message',
            'UMTS_NAS_GMM_State',
            'UMTS_NAS_MM_State',
            ]

arg_dict = [{'file': f, 'msg': m} for f in files for m in msg_list]


#core function that gets the dataframe saved in parser_mi, edits it in the edit function and saves it to df_all. also returns a df for e.g. plotting
def analyze(miAnalyzer, df_name, needed_columns, file_info):
    #after running we can collect values
    df = miAnalyzer.get_core_dataframe(df_name, needed_columns)
    df = df_edit(df, file_info=file_info)

    logging.info(f'Finished with {df_name} df')
    
    return df


#function for renaming, reordering stuff/pretty things
def df_edit(df, file_info, save=True):
    
    #change weird none/nans to np.nan type for consistency
    df[df == 'None'] = np.nan
    df[df == 'nan'] = np.nan

    df.loc[:, 'file'] = file_info

    if save:
        for c in df.columns: #format lists correctly
            if (isinstance(df[c][0], str) and ',' in df[c][0]):
                df[c] = df.apply(lambda row:  row[c].strip('[]').replace('"', '').replace(' ', '').split(',')   , axis=1)
        df.apply(pd.to_numeric, errors='coerce').fillna(df) #make columns numeric if possible

    return df 


def main(file=None, msg_type=None):

    # Parse config
    cfgParser = configparser.ConfigParser()
    cfgParser.read_dict(default_config)

    modem_path = cfgParser["modem_info"].get("device_path")
    baud_rate = cfgParser["modem_info"].getint("baud_rate")
    logging_path = Path(cfgParser.get("logging", "log_file_path"))

    if file is None:
        file_list = list(str(p) for p in logging_path.rglob("monitor*.mi2log"))
    else:
        file_list = [str(logging_path/file)]

    for file in file_list:

        print(f'reading file {file}')
        
        # Initialize a 3G/4G monitor
        src = OfflineReplayer()
    
        src.set_input_path(file)

        miAnalyzer = MiAnalyzer()
        miAnalyzer.set_source(src)

        if msg_type is None:
            src.enable_log_all()
        else:
            src.enable_log(msg_type)

        # Start the monitoring
        src.run()

        #after running we can collect values
        #collect all data and no renaming/editing
        msg_types=miAnalyzer.get_columns()

        monitor_path = Path(file).relative_to(logging_path)
        monitor_file = monitor_path.stem
        out_parent = out_root/monitor_path.parent/monitor_file

        for msg in msg_types: #get all dataframes

            out_parent.mkdir(parents=True, exist_ok=True)
            out_path = out_parent/f"{msg}.pkl"

            df = analyze(miAnalyzer, msg, None, file_info=monitor_file)

            df.to_pickle(str(out_path))
            print(f"Data saved as {out_path}")

            del df
            gc.collect()

    logging.info('finished the Offline Analysis')


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--job-index", "-i", type=int, help="Index of job according to presaved list, from 0 to "
                                                            f"{len(arg_dict)-1}. "
                                                            f"If all-messages set, selects from mi2logfiles "
                                                            f"from 0 to {len(files)-1}.")
    parser.add_argument('--all-messages', "-a", action='store_true', help="Process all message types at once.")

    args = parser.parse_args()

    job_index = args.job_index
    file = None
    msg = None
    if job_index is not None:
        if args.all_messages:
            file = files[job_index]
        else:
            job = arg_dict[job_index]
            file = job['file']
            msg = job['msg']

    main(file=file, msg_type=msg)
