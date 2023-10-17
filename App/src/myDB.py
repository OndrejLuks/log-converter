from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy import create_engine, schema
from sqlalchemy.sql import text
import sys

# ===========================================================================================================
# ===========================================================================================================

class DatabaseHandle:
    def __init__(self, config, interface):
        self.schema_name = config["database"]["schema_name"]
        self.host = config["database"]["host"]
        self.port = config["database"]["port"]
        self.database = config["database"]["database"]
        self.user = config["database"]["user"]
        self.password = config["database"]["password"]
        self.clean = config["settings"]["clean_upload"]
        self.hasPkey = False

        self.conn_string = "postgresql://" + self.user + ":" + self.password + "@" + self.host + "/" + self.database

        self.gui_interface = interface

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
            if not self.gui_interface is None:
                self.gui_interface.print_to_box()
                self.gui_interface.print_to_box(f"WARNING - querry:  {e}\n")

# -----------------------------------------------------------------------------------------------------------

    def connect(self) -> None:
        """Function to handle database connection procedure"""
        try:
            self.engine = create_engine(self.conn_string)
            self.connection = self.engine.connect()

        except Exception as e:
            if not self.gui_interface is None:
                self.gui_interface.print_to_box()
                self.gui_interface.print_to_box(f"DB CONNECTION ERROR:  {e}\n")
                self.gui_interface.exit()

# -----------------------------------------------------------------------------------------------------------    

    def create_schema(self) -> None:
        """Creates schena if not exists"""
        try:
            if self.clean:
                # clean upload is selected
                if self.connection.dialect.has_schema(self.connection, self.schema_name):
                    if not self.gui_interface is None:
                        self.gui_interface.print_to_box(f" - Dropping schema {self.schema_name}\n")
                    self._querry(f"DROP SCHEMA {self.schema_name} CASCADE")

            if not self.connection.dialect.has_schema(self.connection, self.schema_name):
                if not self.gui_interface is None:
                    self.gui_interface.print_to_box(f" - Creating schema {self.schema_name}\n")
                self.connection.execute(schema.CreateSchema(self.schema_name))
                self.connection.commit()

                
        except Exception as e:
            if not self.gui_interface is None:
                self.gui_interface.print_to_box()
                self.gui_interface.print_to_box(f"ERROR - schema:  {e}\n")
                self.gui_interface.exit()
    
# -----------------------------------------------------------------------------------------------------------

    def upload_data(self, data: list) -> None:
        """Uploads given list of dataframes to the database"""
        for df in data:
            try:
                table_name = f"{df.columns.values[0]}"
                if not self.gui_interface is None:
                    self.gui_interface.print_to_box(f"     > uploading signal: {table_name}\n")
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
                if not self.gui_interface is None:
                    self.gui_interface.print_to_box("       - WARNING: Skipping signal upload due to unique violation. This record already exists in the DB.\n")
            
            except Exception as e:
                if not self.gui_interface is None:
                    self.gui_interface.print_to_box()
                    self.gui_interface.print_to_box(f"DB UPLOAD WARNING:  {e}\n")
    
# -----------------------------------------------------------------------------------------------------------

    def finish(self) -> None:
        """Function to handle database connection closing"""
        try:
            if not self.gui_interface is None:
                self.gui_interface.print_to_box("Closing database connection ...  ")
            self.connection.close()
            if not self.gui_interface is None:
                self.gui_interface.print_to_box("done!\n")
            
        except Exception as e:
            if not self.gui_interface is None:
                self.gui_interface.print_to_box()
                self.gui_interface.print_to_box(f"DB CLOSING ERROR:  {e}\n")

