from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy import create_engine, schema
from sqlalchemy.sql import text

# ===========================================================================================================
# ===========================================================================================================

class DatabaseHandle:
    def __init__(self, config, communication, event):
        self.schema_name = config["database"]["schema_name"]
        self.host = config["database"]["host"]
        self.port = config["database"]["port"]
        self.database = config["database"]["database"]
        self.user = config["database"]["user"]
        self.password = config["database"]["password"]
        self.clean = config["settings"]["clean_upload"]
        self.hasPkey = False

        self.conn_string = "postgresql://" + self.user + ":" + self.password + "@" + self.host + "/" + self.database

        self.comm = communication
        self.stop_event = event

# -----------------------------------------------------------------------------------------------------------

    def __del__(self):
        self.finish()

# -----------------------------------------------------------------------------------------------------------
    
    def _querry(self, message: str) -> None:
        """Sends and executes a querry specified in the message to the database."""
        try:
            msg = text(message)
            self.connection.execute(msg)
            self.connection.commit()

        except ProgrammingError:
            # occurs when primary key is attempted to set again
            pass

        except Exception as e:
            self.comm.send_error("WARNING", f"Problem with query:\n{e}", "F")

# -----------------------------------------------------------------------------------------------------------

    def connect(self) -> None:
        """Function to handle database connection procedure"""
        try:
            self.engine = create_engine(self.conn_string)
            self.connection = self.engine.connect()

        except Exception as e:
            self.comm.send_error("ERROR", f"DB CONNECTION ERROR:\n{e}", "T")

# -----------------------------------------------------------------------------------------------------------    

    def create_schema(self) -> None:
        """Creates schena if not exists"""
        try:
            if self.clean:
                # clean upload is selected
                if self.connection.dialect.has_schema(self.connection, self.schema_name):
                    self.comm.send_to_print(f" - Dropping schema {self.schema_name}")
                    self._querry(f"DROP SCHEMA {self.schema_name} CASCADE")

            if not self.connection.dialect.has_schema(self.connection, self.schema_name):
                self.comm.send_to_print(f" - Creating schema {self.schema_name}")
                self.connection.execute(schema.CreateSchema(self.schema_name))
                self.connection.commit()

        except Exception as e:
            self.comm.send_error("ERROR", f"Error with DB schema:\n{e}", "T")
    
# -----------------------------------------------------------------------------------------------------------

    def upload_data(self, data: list) -> None:
        """Uploads given list of dataframes to the database"""
        for df in data:
             # thread end check
            if self.stop_event.is_set():
                print("Database upload aborted.")
                return

            try:
                table_name = f"{df.columns.values[0]}"
                self.comm.send_to_print(f"     > uploading signal: {table_name}")
                df.to_sql(name=table_name,
                            con=self.engine,
                            schema=self.schema_name,
                            index=True,
                            index_label="time_stamp",
                            if_exists="append")
                self.connection.commit()
                # set primary key
                self._querry(f'ALTER TABLE {self.schema_name}."{table_name}" ADD PRIMARY KEY (time_stamp)')

            except IntegrityError:
                self.comm.send_to_print("       - WARNING: Skipping signal upload due to unique violation. This record already exists in the DB.")
            
            except Exception as e:
                self.comm.send_error("WARNING", f"Problem with DB upload:\n{e}", "F")
    
# -----------------------------------------------------------------------------------------------------------

    def finish(self) -> None:
        """Function to handle database connection closing"""
        try:
            self.comm.send_to_print("Closing database connection ...  ", end='')
            self.connection.close()
            self.comm.send_to_print("done!")
            
        except Exception as e:
            self.comm.send_error("WARNING", f"Problem with closing DB:\n{e}", "F")
