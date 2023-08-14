from asammdf import MDF
from sqlalchemy import create_engine, schema
from sqlalchemy.sql import text
import pandas as pd
import os
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
                    print(f"Dropping schema {self.schema_name}")
                    drop_schema_sql = text(f"DROP SCHEMA {self.schema_name} CASCADE")
                    self.connection.execute(drop_schema_sql)
                    self.connection.commit()

            if not self.connection.dialect.has_schema(self.connection, self.schema_name):
                print(f"Creating schema {self.schema_name}")
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
            # self.cursor.close()
            self.connection.close()
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
        return
    
    return data


def create_dbc_set() -> set:
    """Creates a dictionary of all DBC files in format {"CAN":[dbc-file, can-channel]}"""
    converter_db = {
        "CAN": []
    }
    try:
        for dbc_file in os.listdir("DBCfiles"):
            converter_db["CAN"].append((os.path.join("DBCfiles", dbc_file), 0))     # 0 means "apply the database to every BUS"

    except OSError:
        print()
        print("ERROR while loading DBC files. Check for folder existance.")
        return

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
            # remove repeating values, leave only 1st and last in repeating series
            mask = ((df[df.columns.values[0]] != df[df.columns.values[0]].shift()) |(df[df.columns.values[0]] != df[df.columns.values[0]].shift(-1)))
            # leave data every 30 minutes, if previous operation deletes too much
            # time_diffs = df.index.to_series().diff()
            # mask |= time_diffs >= pd.Timedelta(minutes=30)
            # apply mask
            result_df = df[mask]
            result_list.append(result_df)
        
    return result_list


def split_df_by_cols(df) -> set:
    column_df = []
    for col in df.columns:
        column_df.append(pd.DataFrame(df[col]))
    return column_df


def process_handle(dbc_set: set, config) -> bool:
    """Function that handles MF4 files process from conversion to upload"""
    try:
        # prepare the database
        db = DatabaseHandle(config)
    
        if not db.connect():
            return False
        if not db.create_schema():
            return False
        
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

                    print(" done!")
                    print()

        # close database connection
        if not db.finish():
            return False

    except OSError:
        print("ERROR while loading MF4 files. Check for DBC and MF4 existance.")
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
