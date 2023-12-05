# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy import create_engine, schema, inspect
from sqlalchemy.sql import text
from .communication import PipeCommunication
import pandas as pd

# ================================================================================================================================
# ================================================================================================================================

class DatabaseHandle:
    def __init__(self, config, communication: PipeCommunication, event):
        self._comm = communication
        self._stop_event = event
        
        try:
            self._schema_name = config["database"]["schema_name"]
            self._host = config["database"]["host"]
            self._port = config["database"]["port"]
            self._database = config["database"]["database"]
            self._user = config["database"]["user"]
            self._password = config["database"]["password"]
            self._clean = config["settings"]["clean_upload"]

        except Exception as e:
            self._comm.send_error("ERROR", f"Problem with creating db object:\n{e}", "T")
            return

        self._conn_string = "postgresql://" + self._user + ":" + self._password + "@" + self._host + "/" + self._database
        
# --------------------------------------------------------------------------------------------------------------------------------

    def __del__(self):
        self.finish()

# --------------------------------------------------------------------------------------------------------------------------------
    
    def querry(self, message: str, fetch_results: bool) -> list:
        """Sends and executes a querry specified in the message to the database."""
              
        try:
            msg = text(message)
            result = self._connection.execute(msg)
            self._connection.commit()

        except ProgrammingError:
            # occurs when primary key is attempted to set again
            pass

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with query:\n{e}", "F")
            return None
        
        if fetch_results:
            try:
                data = result.fetchall()
                return data
            
            except Exception as e:
                self._comm.send_error("WARNING", f"Problem with query results:\n{e}", "F")
                return []

        return []

# --------------------------------------------------------------------------------------------------------------------------------

    def connect(self) -> None:
        """Function to handle database connection procedure"""
        try:
            self._comm.send_to_print("Connecting to the database ...  ", end='')
            self._engine = create_engine(self._conn_string)
            self._connection = self._engine.connect()
            self._comm.send_to_print("done!")

        except Exception as e:
            self._comm.send_error("ERROR", f"DB CONNECTION ERROR:\n{e}", "T")

# --------------------------------------------------------------------------------------------------------------------------------   

    def create_schema(self) -> None:
        """Creates schena if not exists"""
        try:
            if self._clean:
                # clean upload is selected
                if self._connection.dialect.has_schema(self._connection, self._schema_name):
                    self._comm.send_to_print(f" - Dropping schema {self._schema_name}")
                    self.querry(f"DROP SCHEMA {self._schema_name} CASCADE", False)

            if not self._connection.dialect.has_schema(self._connection, self._schema_name):
                self._comm.send_to_print(f" - Creating schema {self._schema_name}")
                self._connection.execute(schema.CreateSchema(self._schema_name))
                self._connection.commit()

        except Exception as e:
            self._comm.send_error("ERROR", f"Error with DB schema:\n{e}", "T")
    
# --------------------------------------------------------------------------------------------------------------------------------

    def upload_data(self, data: list) -> None:
        """Uploads given list of dataframes to the database"""
        for df in data:
             # thread end check
            if self._stop_event.is_set():
                print("Database upload aborted.")
                return

            try:
                table_name = f"{df.columns.values[0]}"
                self._comm.send_to_print(f"     > uploading signal: {table_name}")
                df.to_sql(name=table_name,
                            con=self._engine,
                            schema=self._schema_name,
                            index=True,
                            index_label="time_stamp",
                            if_exists="append")
                self._connection.commit()
                # set primary key
                self.querry(f'ALTER TABLE {self._schema_name}."{table_name}" ADD PRIMARY KEY (time_stamp)', False)

            except IntegrityError:
                self._comm.send_to_print("       - WARNING: Skipping signal upload due to unique violation. This record already exists in the DB.")
            
            except Exception as e:
                self._comm.send_error("WARNING", f"Problem with DB upload:\n{e}", "F")
    
# --------------------------------------------------------------------------------------------------------------------------------

    def finish(self) -> None:
        """Function to handle database connection closing"""
        try:
            self._comm.send_to_print("Closing database connection ...  ", end='')
            self._connection.close()
            self._comm.send_to_print("done!")
            
        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with closing DB:\n{e}", "F")

# --------------------------------------------------------------------------------------------------------------------------------

    def update_config(self, config) -> None:
        try:
            self._schema_name = config["database"]["schema_name"]
            self._host = config["database"]["host"]
            self._port = config["database"]["port"]
            self._database = config["database"]["database"]
            self._user = config["database"]["user"]
            self._password = config["database"]["password"]
            self._clean = config["settings"]["clean_upload"]

            self._conn_string = "postgresql://" + self._user + ":" + self._password + "@" + self._host + "/" + self._database

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with db config update:\n{e}", "F")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def get_table_names(self) -> list:
        try:
            inspector = inspect(self._engine)
            tbl_names = inspector.get_table_names(schema=self._schema_name)

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with signal fetching:\n{e}", "F")
            return None

        return tbl_names
    
# --------------------------------------------------------------------------------------------------------------------------------

    def save_data(self, tables_str: str, from_time: str, to_time: str, file_path: str) -> None:
        self._comm.send_to_print("Downloading data ...")
        self.connect()

        tables = tables_str.split(";")
        combined_data_frame = pd.DataFrame(columns=["time_stamp"])

        try:
            for tbl in tables:
                qry = f"SELECT * FROM {self._schema_name}.\"{tbl}\" WHERE time_stamp >= '{from_time}' AND time_stamp <= '{to_time}'"

                result = self.querry(qry, True)
                data_frame = pd.DataFrame(result)
                if not data_frame.empty:
                    combined_data_frame = combined_data_frame.merge(data_frame, on="time_stamp", how="outer")

            self.finish()
            combined_data_frame.sort_values(by="time_stamp", inplace=True)
            combined_data_frame.to_csv(file_path, index=False)

            self._comm.send_to_print(f"SUCCESS: Selected data saved to {file_path}")

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with data download:\n{e}", "F")
            return

        return
