# This script takes all the MF4 files from SourceMF4 folder, extracts CAN message using DBC files from DBCfiles
# folder and uploads these extracted data into specified database.
# For database settings change according lines in config.json file.
# It is also possible to aggregate extracted data by adjusting the setting "aggregate" inside config.json to true.
#
# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ==========================================================================================================================
# ==========================================================================================================================


from datetime import timedelta
from threading import Lock
from src import procData, mfd, myDB
from pathlib import Path
import pandas as pd
import os
import sys
import json
import pytz
import shutil
import warnings
import threading
import can_decoder
import canedge_browser


# ===========================================================================================================
# ===========================================================================================================

def open_config():
    """Loads configure json file (config.json) from root directory. Returns json object."""
    try:
        file = open(os.path.join("src", "config.json"), "r")
        data = json.load(file)
        file.close()

    except FileNotFoundError:
        print()
        print("ERROR while reading src\config.json file. Check for file existance.")
        sys.exit(1)
    
    return data


def setup_fs() -> canedge_browser.LocalFileSystem:
    """Sets up a filesystem required for signal extraxtion from raw MF4"""
    base_path = Path(__file__).parent
    return canedge_browser.LocalFileSystem(base_path=base_path)


def convert_mf4(mf4_file: os.path, dbc_list: list, write_info: bool) -> list:
    """Converts and decodes MF4 files to a dataframe using DBC files."""
    fs = setup_fs()
    proc = procData.ProcessData(fs, dbc_list)

    # get raw dataframe from mf4 file
    df_raw, device_id = proc.get_raw_data(mf4_file)

    # replace transport protocol with single frames
    tp = mfd.MultiFrameDecoder("j1939")
    df_raw = tp.combine_tp_frames(df_raw)

    # extract can messages
    df_phys = proc.extract_phys(df_raw)

    # set correct index values
    df_phys.index = pd.to_datetime(df_phys.index)
    df_phys.index = df_phys.index.round('1us')

    # write time info if required
    if write_info:
        print("   - writing time information into MF4-info.csv... ")
        # check if df is not empty
        if df_phys.shape[0] > 0:
            write_time_info(mf4_file, df_phys.index[0], df_phys.index[-1])

    print("   - extracting individual signals... ")
    return split_df_by_cols(df_phys)


def aggregate(df, time_max: int, lock: threading.Lock, dfs: list) -> None:
    """Aggregates input signal dataframe by removing redundant values"""
    num_rows = df.shape[0]

    if num_rows > 0:
        sig_name = df.columns.values[0]
        with lock:
            print(f"     > started aggregating signal: {sig_name}")
        # create an array of indexes to use as a mask for the dataframe
        idx_array = []
        # insert first index into the array
        previous = 0
        idx_array.append(previous)
        # iterate through indexes and store them only if the value changes,
        # or if the time gap exceeds given seconds
        for idx in range(num_rows):
            time_diff = df.index[idx] - df.index[previous]
            if (df.iat[previous, 0] != df.iat[idx, 0]):
                idx_array.append(idx-1)
                idx_array.append(idx)
                previous = idx
            elif (time_diff > timedelta(seconds=time_max)):
                idx_array.append(idx)
                previous = idx

        # add last item into the mask
        idx_array.append(num_rows - 1)
        # create a new dataframe and remove duplicates
        result_df = df.iloc[list(dict.fromkeys(idx_array))]
        
        # safely store the aggregated signal
        with lock:
            dfs.append(result_df)
            print(f"     = finished agg. signal: {sig_name}")
                

def split_df_by_cols(df) -> list:
    """Extracts and returns individual signals from given converted physica-value-dataframe"""
    column_df = []

    if not 'Signal' in df.columns:
        # No signals were converted
        return column_df

    for signal_name in df['Signal'].unique():
        signal_df = df[df['Signal'] == signal_name][['Physical Value']].copy()
        signal_df.rename(columns={'Physical Value': signal_name}, inplace=True)
        column_df.append(signal_df)

    return column_df

# -----------------------------------------------------------------------------------------------------------

def write_time_info(file: str, start_time, end_time) -> None:
    """Writes start and end timestamp information about inputted file into MF4-info.csv"""

    try:
        file_name = os.path.relpath(file, "SourceMF4")
        prg_timezone = pytz.timezone('Europe/Prague')
        start_time = start_time.astimezone(prg_timezone)
        end_time = end_time.astimezone(prg_timezone)

        # create header if file does not exist
        if not os.path.exists("MF4-info.csv"):
            with open('MF4-info.csv', 'a') as f:
                f.write("file_name,recorded_from,recorded_to\n")

        # write file informatin
        with open('MF4-info.csv', 'a') as f:
            f.write(file_name + "," + str(start_time) + "," + str(end_time) + "\n")

    except Exception as e:
        print()
        print(f"INFO RECORDING WARNING:  {e}") 


def get_MF4_files() -> list:
    """Generates a list of paths to all found MF4 files in the SourceMF4 folder. Returns also the number of found files."""
    out = []
    try:
        # search for MF4 files
        for root, dirs, files in os.walk("SourceMF4"):
            # mostly "files" consists of only 1 file
            for file in files:
                if file.endswith(".MF4"):
                    # found MF4 file
                    mf4_file = os.path.join(root, file)
                    out.append(mf4_file)

    except Exception as e:
        print()
        print(f"MF4 READING WARNING:  {e}") 
        sys.exit(1)

    if len(out) == 0:
        print()
        print("WARNING: No MF4 files found!")
        print()

    return out, len(out)


def create_dbc_list() -> list:
    """""Creates a list of loaded DBC files via can_decoder"""""

    db_list = []
    try:
        dir = os.listdir("DBCfiles")
        if len(dir) == 0:
            raise OSError

        for dbc_file in dir:
            if dbc_file.endswith(".dbc"):
                db = can_decoder.load_dbc(os.path.join("DBCfiles", dbc_file))
                db_list.append(db)

    except OSError:
        print()
        print("ERROR while loading DBC files. Check for file existance.")
        sys.exit(1)

    return db_list


def rm_empty_subdirs(top_level: str) -> None:
    """Removes empty directories in given root"""
    try:
        for root, dirs, files in os.walk(top_level, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
    except OSError:
        print()
        print(f"ERROR: Failed to remove empty subdirs of root {top_level}")
        sys.exit(1)


def move_done_file(file: os.path) -> None:
    """Moves given file from SourceMF4 folder to DoneMF4 folder"""
    # get target file path
    target_file = file.replace("SourceMF4", "DoneMF4")
    # get and create target directory
    target_dir = os.path.dirname(target_file)
    create_dir(target_dir)

    try:
        # move the file
        shutil.move(file, target_file)

    except Exception as e:
        print()
        print(f"FILE MOVING WARNING:  {e}")

    # remove empty source folders
    rm_empty_subdirs("SourceMF4")


def create_dir(target_dir: str) -> None:
    """Creates given directory if it doesn't exist"""
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    except Exception as e:
        print()
        print(f"DIR CREATION WARNING:  {e}") 

# -----------------------------------------------------------------------------------------------------------

def process_handle(dbc_list: set, config) -> None:
    """Function that handles MF4 files process from conversion to upload"""
    
    # prepare the database
    db = myDB.DatabaseHandle(config)
    db.connect()
    db.create_schema()
    
    # load MF4 files
    mf4_file_list, num_of_mf4_files = get_MF4_files()
    num_of_done_mf4_files = 0

    try: 
        for file in mf4_file_list:
            # CONVERT FILE into Signal files
            print(f" - Converting: {file}")
        
            dfs_to_upload = []
            converted_files = convert_mf4(file, dbc_list, config["settings"]["write_time_info"])

            # AGGREGATE if requested
            if config["settings"]["aggregate"]:
                threads = []
                print("   - aggregating... ")
                # run each signal in a different thread
                lock = Lock()
                for signal_df in converted_files:
                    thread = threading.Thread(target=aggregate, args=(signal_df, config["settings"]["agg_max_skip_seconds"], lock, dfs_to_upload))
                    threads.append(thread)
                    thread.start()
                
                # wait for threads to finish
                for thr in threads:
                    thr.join()
            
            else:
                dfs_to_upload = converted_files

            # UPLOAD TO DB
            print("   - uploading... ")
            db.upload_data(dfs_to_upload)
  
            # MOVE DONE FILES if requested
            if config["settings"]["move_done_files"]:
                print("   - moving the file... ")
                move_done_file(file)

            num_of_done_mf4_files += 1
            print(f"   - DONE!     Overall progress:  {round((num_of_done_mf4_files / num_of_mf4_files)*100, 2)} %")
            print()

    except Exception as e:
        print()
        print(f"Process ERROR:  {e}")
        sys.exit(1)

# -----------------------------------------------------------------------------------------------------------

def prompt_warning(schema_name) -> None:
    """Propmts warning if the 'clean_upload' setting is set to true"""
    print()
    print(" ! WARNING ! WARNING ! WARNING ! WARNING ! WARNING ! WARNING !")
    print()
    print(f'   YOU ARE ABOUT TO DELETE THE CURRENT {schema_name} SCHEMA')
    print('   Do you really want to proceed?')
    print()
    print('   Enter "y" for YES or "n" for NO:  ', end="")

    while(True):
        resp = input()
        if resp == 'y' or resp == 'Y':
            print('   Okay.')
            print()
            break
        elif resp == 'n' or resp == 'N':
            print('   Change the settings.clean_upload to "false" in src\config.json file')
            print()
            sys.exit(0)
        else:
            print('   Unknown response. Try again, please:  ', end='')

# -----------------------------------------------------------------------------------------------------------

def warning_handler(message, category, filename, lineo, file=None, line=None) -> None:
    """Handles warnings for more compact vizualization. Mostly only because of blank signal convertion."""
    print(f"     - warning: {message}")

# ===========================================================================================================

def main():
    warnings.showwarning = warning_handler
    print()
    # read configuration
    print("Reading config file ...  ", end="")
    config = open_config()
    print("done!")

    # prompt warning when clean database is selected
    if config["settings"]["clean_upload"]:
        prompt_warning(config["database"]["schema_name"])

    # read all DBC files
    print("Reading all DBC files ...  ", end="")
    dbc_list = create_dbc_list()
    print("done!")

    # convert and upload MF4 files
    print("Converting, decoding and uploading the MF4 files ...")
    process_handle(dbc_list, config)

    print()
    print("                                      ~ ")           
    print("Everything completed successfully!  c[_]")
    print()


# ===========================================================================================================

if __name__ == '__main__':
    main()
