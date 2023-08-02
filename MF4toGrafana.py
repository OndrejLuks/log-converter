from asammdf import MDF
import cantools as ct
import pandas as pd
import os
import json

# ===========================================================================================================
# ===========================================================================================================

def open_config():
    """Loads configure json file (config.json) from root directory. Returns json object."""
    try:
        file = open("config.json")
        data = json.load(file)
        file.close()
    except FileNotFoundError:
        print("ERROR while reading config.json file. Check for file existance.")
        return
    
    return data


def create_dbc_set() -> set:
    """Creates a dictionary of all DBC files in format {"CAN":[dbc-file, can-channel]}"""
    converter_db = {
        "CAN": []
    }
    try:
        for dbc_file in os.listdir("DBCfiles"):
            # TODO - WHAT ABOUT BUS?
            converter_db["CAN"].append((dbc_file, 1))

    except OSError:
        print("ERROR while loading DBC files. Check for folder existance.")
        return

    return converter_db


def convert_mf4(mf4_file: os.path, dbc_set: set) -> pd.DataFrame:
    """Converts and decodes MF4 files to a dataframe using DBC files."""
    # convert MF4 to MDF
    mdf = MDF(mf4_file)
    # extract CAN messages
    extracted_mdf = mdf.extract_bus_logging(dbc_set)
    # return MDF converted to dataframe
    return extracted_mdf.to_dataframe()


def aggregate(df_set) -> set:
    for df in df_set:
        # TODO AGGREGATION 
        continue
    
    return df_set


def split_df_by_cols(df) -> set:
    column_df = []
    for col in df.columns:
        column_df.append(pd.DataFrame(df[col]))
    return column_df


def process_handle(dbc_set: set, config) -> bool:
    try:
        # search for MF4 files
        for root, dirs, files in os.walk("SourceMF4"):
            # mostly "files" consists of only 1 file
            for file in files:
                if file.endswith(".MF4"):
                    # found MF4 file
                    mf4_file = os.path.join(root, file)
                    print(f" - Working on: {mf4_file}")

                    # decode and convert MF4 file
                    print("               decoding... ", end="")
                    mf4_df = convert_mf4(mf4_file, dbc_set)

                    # split dataframe by different signals
                    column_dataframes = split_df_by_cols(mf4_df)

                    # aggregate if neccessary
                    if config["settings"]["aggregate"]:
                        print("aggregating... ", end="")
                        mf4_df = aggregate(column_dataframes)

                    # upload to the db
                    print("uploading... ", end="")
                    # TODO

                    print(" done!")
                    print()

    except OSError:
        print("ERROR while loading MF4 files. Check for folder existance.")
        return False
    
    return True

# ===========================================================================================================

def main():
    print()
    # read configuration
    print("Reading config file ...  ", end="")
    config = open_config()
    print("done!")

    # read all DBC files
    print("Reading all DBC files ...  ", end="")
    dbc_set = create_dbc_set()
    print("done!")

    # convert and upload MF4 files
    print("Converting, decoding and uploading the MF4 files ...")
    if not process_handle(dbc_set, config):
        return
    
    print("                                      ~ ")           
    print("Everything completed successfully!  c[_]")
    print()


# ===========================================================================================================

if __name__ == '__main__':
    main()