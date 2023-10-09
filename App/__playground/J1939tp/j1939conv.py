from asammdf import MDF
from utils import procData, mfd
from pathlib import Path
import pandas as pd
import os
import sys
import can_decoder
import canedge_browser
import mdf_iter

mdf_path = "00000004_fin.MF4"
dbc_path = "Inventus_BMS_Interface_ntc.dbc"

def setup_fs():
    base_path = Path(__file__).parent
    return canedge_browser.LocalFileSystem(base_path=base_path)


def load_dbc_files(dbc_paths: list) -> list:
    db_list = []
    for dbc in dbc_paths:
        db = can_decoder.load_dbc(dbc)
        db_list.append(db)

    return db_list

def convert_mf4() -> None:
    fs = setup_fs()
    db_list = load_dbc_files([dbc_path])
    proc = procData.ProcessData(fs, db_list)

    output_folder = "output" + mdf_path.replace(".MF4", "")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df_raw, device_id = proc.get_raw_data(mdf_path)
    df_raw.to_csv(os.path.join(output_folder, "tp_raw_data.csv"))

    # replace transport protocol with single frames
    tp = mfd.MultiFrameDecoder("j1939")
    df_raw = tp.combine_tp_frames(df_raw)
    df_raw.to_csv(os.path.join(output_folder, "tp_raw_data_combined.csv"))

    # extract can messages
    df_phys = proc.extract_phys(df_raw)
    df_phys.to_csv(os.path.join(output_folder, "tp_extracted.csv"))


convert_mf4()