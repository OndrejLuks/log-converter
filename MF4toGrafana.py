# This script takes all the MF4 files from SourceMF4 folder, extracts CAN message using DBC files from DBCfiles
# folder and uploads these extracted data into specified database.
# For database settings change according lines in config.json file.
# It is also possible to aggregate extracted data by adjusting the setting "aggregate" inside config.json to true.
#
# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# INTRUSIVE CAN MESSAGE:
# BA_DEF_ BO_  "VFrameFormat" ENUM  "StandardCAN","ExtendedCAN","reserved","J1939PG"

# ==========================================================================================================================
# ==========================================================================================================================

from asammdf import MDF
from sqlalchemy import create_engine, schema
from sqlalchemy.sql import text
import pandas as pd
import os
import sys
import json

# ===========================================================================================================
# ===========================================================================================================

class DatabaseHandle:
    def __init__(self, config):
        self.schema_name = config["database"]["schema_name"]
        self.host = config["database"]["host"]
        self.port = config["database"]["port"]
        self.database = config["database"]["database"]
        self.user = config["database"]["user"]
        self.password = config["database"]["password"]
        self.clean = config["settings"]["clean_upload"]

        self.conn_string = "postgresql://" + self.user + ":" + self.password + "@" + self.host + "/" + self.database


    def __del__(self):
        self.finish()


    def connect(self) -> bool:
        try:
            self.engine = create_engine(self.conn_string)
            self.connection = self.engine.connect()

        except Exception as e:
            print()
            print(f"ERROR: {e}")
            return False
        
        return True
    

    def create_schema(self) -> bool:
        try:
            if self.clean:
                if self.connection.dialect.has_schema(self.connection, self.schema_name):
                    print(f" - Dropping schema {self.schema_name}")
                    drop_schema_sql = text(f"DROP SCHEMA {self.schema_name} CASCADE")
                    self.connection.execute(drop_schema_sql)
                    self.connection.commit()

            if not self.connection.dialect.has_schema(self.connection, self.schema_name):
                print(f" - Creating schema {self.schema_name}")
                self.connection.execute(schema.CreateSchema(self.schema_name))
                self.connection.commit()

                
        except Exception as e:
            print()
            print(f"ERROR: {e}")
            return False
        
        return True
    

    def upload_data(self, data: list) -> bool:
        try:
            for idx, df in enumerate(data):
                table_name = f"{df.columns.values[0]}"
                df.to_sql(name=table_name,
                          con=self.engine,
                          schema=self.schema_name,
                          index=True,
                          index_label="time_stamp",
                          if_exists="append")
                self.connection.commit()

        except Exception as e:
            print()
            print(f"ERROR: {e}")
            return False
        
        return True
    

    def finish(self) -> bool:
        try:
            print("Closing database connection ...  ", end="")
            self.connection.close()
            print("done!")
            
        except Exception as e:
            print()
            print(f"ERROR: {e}")
            return False
        
        return True

# ===========================================================================================================
# ===========================================================================================================

def open_config():
    """Loads configure json file (config.json) from root directory. Returns json object."""
    try:
        file = open("config.json")
        data = json.load(file)
        file.close()
    except FileNotFoundError:
        print()
        print("ERROR while reading config.json file. Check for file existance.")
        sys.exit(1)
    
    return data


def check_dbc_file(dbc_file: os.path) -> None:
    """Ugly hotfix function. Deletes a specific line in DBC files if the line is present.
    Presence of this line forbids proper can signal extraction."""
    
    # read all the lines
    with open(dbc_file, 'r') as file:
        lines = file.readlines()

    # write only correct ones
    with open(dbc_file, 'w') as file:
        for line in lines:
            if 'BA_DEF_ BO_  "VFrameFormat" ENUM  "StandardCAN","ExtendedCAN","reserved","J1939PG"' not in line:
                file.write(line)
            else:
                print("(Deleting intrusive line in DBC file)  ", end="")


def create_dbc_set() -> set:
    """Creates a dictionary of all DBC files in format {"CAN":[dbc-file, can-channel]}"""

    converter_db = {
        "CAN": []
    }
    try:
        dir = os.listdir("DBCfiles")
        if len(dir) == 0:
            raise OSError

        for dbc_file in dir:
            check_dbc_file(os.path.join("DBCfiles", dbc_file))
            converter_db["CAN"].append((os.path.join("DBCfiles", dbc_file), 0))     # 0 means "apply the database to every BUS"

    except OSError:
        print()
        print("ERROR while loading DBC files. Check for file existance.")
        sys.exit(1)

    return converter_db


def convert_mf4(mf4_file: os.path, dbc_set: set) -> pd.DataFrame:
    """Converts and decodes MF4 files to a dataframe using DBC files."""
    # convert MF4 to MDF
    mdf = MDF(mf4_file)
    # extract CAN messages
    extracted_mdf = mdf.extract_bus_logging(database_files=dbc_set)
    # return MDF converted to dataframe
    mdf_df = extracted_mdf.to_dataframe(time_from_zero=False, time_as_date=True)
    mdf_df.index = pd.to_datetime(mdf_df.index)

    return mdf_df


def aggregate(df_set) -> set:
    """Aggregates input set of dataframes by removing redundant values"""
    result_list = []
    for df in df_set:
        if df.shape[0] > 0:
            # create an array of indexes to use as a mask for the dataframe
            idx_array = []
            # insert first index into the array
            previous = 0
            idx_array.append(previous)
            
            for idx in range(df.shape[0]):
                if df.iloc[previous, 0] != df.iloc[idx, 0]:
                    idx_array.append(idx-1)
                    idx_array.append(idx)
                    previous = idx
            # add last item into the mask
            idx_array.append(df.shape[0] - 1)
            # remove duplicates and create a new dataframe
            result_list.append(df.iloc[list(dict.fromkeys(idx_array))])
                
    return result_list


def split_df_by_cols(df) -> set:
    column_df = []
    for col in df.columns:
        column_df.append(pd.DataFrame(df[col]))

    return column_df


def count_files_in_dir(dir: str, end: str) -> int:
    count = 0
    try:
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.endswith(end):
                    count += 1
        if count == 0:
            raise OSError

    except OSError:
        print(f"ERROR while loading MF4 files. Check for {dir} or {end} file existance.")
        sys.exit(1)

    return count


def process_handle(dbc_set: set, config) -> bool:
    """Function that handles MF4 files process from conversion to upload"""
    try:
        # prepare the database
        db = DatabaseHandle(config)
    
        if not db.connect():
            return False
        if not db.create_schema():
            return False
        
        num_of_files = count_files_in_dir("SourceMF4", ".MF4")
        num_of_done_files = 0
        
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
                        column_dataframes = aggregate(column_dataframes)
                    
                    # upload to the db
                    print("uploading... ", end="")
                    if not db.upload_data(column_dataframes):
                        return False
                    
                    num_of_done_files += 1

                    print(" done!", end="")
                    print(f"   {round((num_of_done_files / num_of_files) * 100, 2)} %")
                    print()

    except OSError:
        print("ERROR while loading MF4 files. Check for SourceMF4 folder existance.")
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
    
    print()
    print("                                      ~ ")           
    print("Everything completed successfully!  c[_]")
    print()


# ===========================================================================================================

if __name__ == '__main__':
    main()
