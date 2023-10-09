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
from sqlalchemy import create_engine, schema, Table, MetaData
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.sql import text
from datetime import timedelta
from threading import Lock
import pandas as pd
import os
import sys
import json
import shutil
import threading

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
        self.hasPkey = False

        self.conn_string = "postgresql://" + self.user + ":" + self.password + "@" + self.host + "/" + self.database


    def __del__(self):
        self.finish()

    
    def _querry(self, message: str) -> None:
        try:
            msg = text(message)
            self.connection.execute(msg)
            self.connection.commit()

        except ProgrammingError:
            print("       - pkey already set")

        except Exception as e:
            print()
            print(f"WARNING: {e}")

    
    def setPkey(self, data: list) -> None:
        for df in data:
                table_name = f"{df.columns.values[0]}"
                self._querry(f'ALTER TABLE {self.schema_name}."{table_name}" ADD PRIMARY KEY (time_stamp)')
        
        self.hasPkey = True


    def connect(self) -> bool:
        try:
            self.engine = create_engine(self.conn_string)
            self.connection = self.engine.connect()
            self.meta = MetaData()

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
                    self._querry(f"DROP SCHEMA {self.schema_name} CASCADE")

            if not self.connection.dialect.has_schema(self.connection, self.schema_name):
                print(f" - Creating schema {self.schema_name}")
                self.connection.execute(schema.CreateSchema(self.schema_name))
                self.connection.commit()

                
        except Exception as e:
            print()
            print(f"ERROR: {e}")
            return False
        
        return True
    

    def upload_data(self, data: list) -> None:
        for df in data:
            try:
                table_name = f"{df.columns.values[0]}"
                print(f"     > uploading signal: {table_name}")
                df.to_sql(name=table_name,
                            con=self.engine,
                            schema=self.schema_name,
                            index=True,
                            index_label="time_stamp",
                            if_exists="append")
                self.connection.commit()
                # set primary key
                self._querry(f'ALTER TABLE {self.schema_name}."{table_name}" ADD PRIMARY KEY (time_stamp)')

            except ProgrammingError:
                # primary key is already set
                pass

            except IntegrityError:
                print("       - WARNING: Skipping signal upload due to unique violation. This record already exists in the DB.")
            
            except Exception as e:
                print()
                print(f"WARNING: {e}")
    

    def finish(self) -> None:
        try:
            print("Closing database connection ...  ", end="")
            self.connection.close()
            print("done!")
            
        except Exception as e:
            print()
            print(f"ERROR: {e}")        


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


def get_converted_files() -> list:
    out = []
    dir = os.listdir(os.path.join("Temp", "converted"))

    if len(dir) == 0:
        print("   WARNING: No signals were converted")
    
    for file in dir:
        if file.endswith(".parquet"):
            out.append(os.path.join("Temp", "converted", file))
    
    return out


def get_aggregated_dfs() -> pd.DataFrame:
    files = []
    out = []
    dir = []
    # get all .parquet files
    target_dir = os.path.join("Temp", "aggregated")
    if os.path.exists(target_dir):
        dir = os.listdir(target_dir)

    for file in dir:
        if file.endswith(".parquet"):
            files.append(os.path.join("Temp", "aggregated", file))

    
    files.sort()

    for file in files:
        agg_signal_df = pd.read_parquet(file, engine="pyarrow")
        agg_signal_df.index = pd.to_datetime(agg_signal_df.index)
        out.append(agg_signal_df)

    return out


def create_dbc_set() -> dict:
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


def store_multisignal_df(big_df: pd.DataFrame, name: str):
    target_dir = os.path.join("Temp", "converted")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    columns_dfs = split_df_by_cols(big_df)

    for df in columns_dfs:
        df.to_parquet(f'{os.path.join(target_dir, name)}-{df.columns.values[0]}.parquet', engine="pyarrow", index=True)


def convert_mf4(mf4_file: os.path, dbc_set: set, name: str) -> None:
    """Converts and decodes MF4 files to a dataframe using DBC files."""
    # convert MF4 to MDF
    mdf = MDF(mf4_file)

    # extract CAN messages
    extracted_mdf = mdf.extract_bus_logging(database_files=dbc_set)
    # return MDF converted to dataframe
    mdf_df = extracted_mdf.to_dataframe(time_from_zero=False, time_as_date=True)
    mdf_df.index = pd.to_datetime(mdf_df.index)
    mdf_df.index = mdf_df.index.round('1us')
    
    store_multisignal_df(mdf_df, name)


def aggregate(df, time_max: int, name: str, lock: threading.Lock) -> None:
    """Aggregates input signal dataframe by removing redundant values"""
    # iterate signals
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

        target_dir = os.path.join("Temp", "aggregated")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        with lock:
            result_df.to_parquet(f'{os.path.join(target_dir, name)}-{sig_name}.parquet', engine="pyarrow", index=True)
            print(f"     = finished agg. signal: {sig_name}")
                

def split_df_by_cols(df) -> list:
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


def rm_tree_if_exist(root: list) -> None:
    try:
        for dir in root:
            if os.path.exists(dir):
                shutil.rmtree(dir)
    except OSError:
        print()
        print(f"ERROR: Failed to remove tree of root {root}")
        sys.exit(1)


def rm_empty_subdirs(top_level: str) -> None:
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
    # move the given file to DoneMF4
    target_file = file.replace("SourceMF4", "DoneMF4")
    target_dir = os.path.dirname(target_file)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    shutil.move(file, target_file)

    # remove empty source folders
    rm_empty_subdirs("SourceMF4")


def process_handle(dbc_set: set, config) -> bool:
    """Function that handles MF4 files process from conversion to upload"""
    try:
        # prepare the database
        db = DatabaseHandle(config)
    
        if not db.connect():
            return False
        if not db.create_schema():
            return False
        
        if os.path.exists("Temp"):
            shutil.rmtree("Temp")
        
        mf4_file_list = []
        
        # search for MF4 files
        for root, dirs, files in os.walk("SourceMF4"):
            # mostly "files" consists of only 1 file
            for file in files:
                if file.endswith(".MF4"):
                    # found MF4 file
                    mf4_file = os.path.join(root, file)
                    mf4_file_list.append(mf4_file)
        
        num_of_mf4_files = len(mf4_file_list)
        num_of_done_mf4_files = 0
        
        if num_of_mf4_files == 0:
            print("WARNING: No MF4 files found!")

        for idx, file in enumerate(mf4_file_list):
            # CONVERT FILE into Signal files
            print(f" - Converting: {file}")
            convert_mf4(file, dbc_set, str(idx))

            dfs_to_upload = []
            converted_files = get_converted_files()

            if config["settings"]["aggregate"]:
                threads = []
                print("   - aggregating... ")

                for signal_file in converted_files:
                    signal_df = pd.read_parquet(signal_file, engine="pyarrow")
                    signal_df.index = pd.to_datetime(signal_df.index)
                    lock = Lock()
                    thread = threading.Thread(target=aggregate, args=(signal_df, config["settings"]["agg_max_skip_seconds"], str(signal_file.split("-")[0].split("\\")[2]), lock))
                    threads.append(thread)
                    thread.start()
                
                # wait for threads to finish
                for thr in threads:
                    thr.join()

                # get dataframes to upload
                dfs_to_upload = get_aggregated_dfs()
            
            else:
                for idx, fle in enumerate(converted_files):
                    converted_df = pd.read_parquet(fle, engine="pyarrow")
                    converted_df.index = pd.to_datetime(converted_df.index)

                    # assign signal dataframes to upload
                    dfs_to_upload.append(converted_df)

            print("   - uploading... ")
            db.upload_data(dfs_to_upload)
  
            print("   - moving the file... ")
            move_done_file(file)

            # delete temp folders
            rm_tree_if_exist([os.path.join("Temp", "converted"), os.path.join("Temp", "aggregated")])

            num_of_done_mf4_files += 1
            print(f"   - DONE!     Overall progress:  {round((num_of_done_mf4_files / num_of_mf4_files)*100, 2)} %")
            print()


    except OSError:
        print()
        print("ERROR in process_handle function while dealing with files")
        return False
    
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        return False
    
    return True


def prompt_warning(schema_name) -> None:
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
            print('   Change the settings.clean_upload to "false" in config.json file')
            print()
            sys.exit(0)
        else:
            print('   Unknown response. Try again, please:  ', end='')

# ===========================================================================================================

def main():
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
