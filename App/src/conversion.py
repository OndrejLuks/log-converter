# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from datetime import timedelta
from threading import Lock

from .mfd import MultiFrameDecoder
from .utils import Utils
from .proc_data import ProcessData
from .db_handle import DatabaseHandle
from .communication import PipeCommunication

from pathlib import Path
import pandas as pd
import os
import threading
import can_decoder
import canedge_browser

# ================================================================================================================================
# ================================================================================================================================


class Conversion():
    def __init__(self, utilities: Utils,
                 communication: PipeCommunication,
                 database: DatabaseHandle,
                 stop_ev: threading.Event, 
                 thrs: list,
                 config):
        self._utils = utilities
        self._comm = communication
        self._stop_event = stop_ev
        self._db = database
        self._threads = thrs

        self._config = config
        self._dbc_list = None
        
# --------------------------------------------------------------------------------------------------------------------------------

    def create_dbc_list(self) -> list:
        """""Creates a list of loaded DBC files via can_decoder"""""

        db_list = []
        try:
            dir = os.listdir(self._config["settings"]["dbc_path"])
            if len(dir) == 0:
                raise OSError

            for dbc_file in dir:
                if dbc_file.endswith(".dbc"):
                    db = can_decoder.load_dbc(os.path.join(self._config["settings"]["dbc_path"], dbc_file))
                    db_list.append(db)

        except OSError:
            self._comm.send_error("ERROR", "Can't load DBC files. Check for file existance.", "T")

        except Exception as e:
            self._comm.send_error("ERROR", f"Problem with DBC files loading:\n{e}", "T")

        return db_list

# --------------------------------------------------------------------------------------------------------------------------------

    def update_config(self, config) -> None:
        self._config = config
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _setup_fs(self) -> canedge_browser.LocalFileSystem:
        """Sets up a filesystem required for signal extraxtion from raw MF4"""
        base_path = Path(__file__).parent
        return canedge_browser.LocalFileSystem(base_path=base_path)

# --------------------------------------------------------------------------------------------------------------------------------

    def _convert_mf4(self, mf4_file: os.path) -> list:
        """Converts and decodes MF4 files to a dataframe using DBC files."""
        try:
            fs = self._setup_fs()
            proc = ProcessData(fs, self._dbc_list)

            # thread end check
            if self._stop_event.is_set():
                print("Conversion aborted.")
                return None

            # get raw dataframe from mf4 file
            df_raw, device_id = proc.get_raw_data(mf4_file)

            # thread end check
            if self._stop_event.is_set():
                print("Conversion aborted.")
                return None

            # replace transport protocol with single frames
            tp = MultiFrameDecoder("j1939")
            df_raw = tp.combine_tp_frames(df_raw)

            # thread end check
            if self._stop_event.is_set():
                print("Conversion aborted.")
                return None

            # extract can messages
            df_phys = proc.extract_phys(df_raw)

            # thread end check
            if self._stop_event.is_set():
                print("Conversion aborted.")
                return None

            # set correct index values
            df_phys.index = pd.to_datetime(df_phys.index)
            df_phys.index = df_phys.index.round('1us')

            # thread end check
            if self._stop_event.is_set():
                print("Conversion aborted.")
                return None

            # write time info if required
            if self._config["settings"]["write_time_info"] == "true":
                self._comm.send_to_print("   - writing time information into MF4-info.csv...")
                # check if df is not empty
                if df_phys.shape[0] > 0:
                    self._utils.write_time_info(mf4_file, df_phys.index[0], df_phys.index[-1])
        
        except Exception as e:
            self._comm.send_error("ERROR", f"Problem in MF4 conversion:\n{e}", "T")
            return []

        self._comm.send_to_print("   - extracting individual signals...")
        return self._split_df_by_cols(df_phys)

# --------------------------------------------------------------------------------------------------------------------------------

    def _aggregate(self, df, lock: threading.Lock, dfs: list) -> None:
        """Aggregates input signal dataframe by removing redundant values"""

        # thread end check
        if self._stop_event.is_set():
            with lock:
                print("Aggregation thread stopped.")
            return

        num_rows = df.shape[0]

        if num_rows > 0:
            sig_name = df.columns.values[0]
            with lock:
                self._comm.send_to_print(f"     > started aggregating signal: {sig_name}")
            # create an array of indexes to use as a mask for the dataframe
            idx_array = []
            # insert first index into the array
            previous = 0
            idx_array.append(previous)
            # iterate through indexes and store them only if the value changes,
            # or if the time gap exceeds given seconds
            for idx in range(num_rows):
                # thread end check
                if self._stop_event.is_set():
                    with lock:
                        print("Aggregation thread stopped.")
                    return

                time_diff = df.index[idx] - df.index[previous]
                if (df.iat[previous, 0] != df.iat[idx, 0]):
                    idx_array.append(idx-1)
                    idx_array.append(idx)
                    previous = idx
                elif (time_diff > timedelta(seconds=int(self._config["settings"]["agg_max_skip_seconds"]))):
                    idx_array.append(idx)
                    previous = idx

            # add last item into the mask
            idx_array.append(num_rows - 1)
            # create a new dataframe and remove duplicates
            result_df = df.iloc[list(dict.fromkeys(idx_array))]

            # thread end check
            if self._stop_event.is_set():
                with lock:
                    print("Aggregation thread stopped.")
                return
            
            # safely store the aggregated signal
            with lock:
                dfs.append(result_df)
                self._comm.send_to_print(f"     = finished agg. signal: {sig_name}")

            return

# --------------------------------------------------------------------------------------------------------------------------------          

    def _split_df_by_cols(self, df) -> list:
        """Extracts and returns individual signals from given converted physica-value-dataframe"""
        column_df = []

        if not 'Signal' in df.columns:
            # No signals were converted
            return column_df
        
        try:
            for signal_name in df['Signal'].unique():
                # thread end check
                if self._stop_event.is_set():
                    print("Conversion aborted.")
                    return None

                signal_df = df[df['Signal'] == signal_name][['Physical Value']].copy()
                signal_df.rename(columns={'Physical Value': signal_name}, inplace=True)
                column_df.append(signal_df)

        except Exception as e:
            self._comm.send_error("ERROR", f"Can't split df:\n{e}", "T")
            return []

        return column_df

# --------------------------------------------------------------------------------------------------------------------------------
    
    def check_db_override(self) -> None:
        # check DB override
        if self._config["settings"]["clean_upload"] == "true":
            type = "WARNING!"
            msg = 'With "Clean upload" enabled, the whole current database will be erased!'
            ques = "Do you really want to proceed?"
            self._comm.send_command(f"POP-ACK#{type}#{msg}#{ques}")
        
        else:
            # run the process
            self._comm.send_command("ACK")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def process_handle(self) -> None:
        """Function that handles MF4 files process from conversion to upload"""

        self._comm.send_command("START")

        # load DBC files
        self._dbc_list = self.create_dbc_list()

        # prepare the database
        self._db.connect()
        self._db.create_schema()

        # thread end check
        if self._stop_event.is_set():
            print("Process thread stopped.")
            return

        # load MF4 files
        mf4_file_list, num_of_mf4_files = self._utils.get_MF4_files(self._config["settings"]["mf4_path"])
        num_of_done_mf4_files = 0

        try: 
            for file in mf4_file_list:
                # clear the output textbox
                self._comm.send_command("CLS")

                # thread end check
                if self._stop_event.is_set():
                    print("Process thread stopped.")
                    return

                # CONVERT FILE into Signal files
                self._comm.send_to_print(f" - Converting: {file}")
            
                dfs_to_upload = []
                converted_files = self._convert_mf4(file)

                # thread end check
                if self._stop_event.is_set():
                    print("Process thread stopped.")
                    return

                # AGGREGATE if requested
                if self._config["settings"]["aggregate"] == "true":
                    agg_threads = []
                    self._comm.send_to_print("   - aggregating...")
                    # run each signal in a different thread
                    lock = Lock()
                    for signal_df in converted_files:
                        # thread end check
                        if self._stop_event.is_set():
                            print("Process thread stopped.")
                            return None

                        thread = threading.Thread(target=self._aggregate, args=(signal_df, lock, dfs_to_upload))
                        thread.start()
                        agg_threads.append(thread)
                        self._threads.append(thread)
                    
                    # wait for aggregation threads to finish
                    for thr in agg_threads:
                        thr.join()
                
                else:
                    dfs_to_upload = converted_files

                # thread end check
                if self._stop_event.is_set():
                    print("Process thread stopped.")
                    return

                # UPLOAD TO DB
                self._comm.send_to_print("   - uploading...")
                self._db.upload_data(dfs_to_upload)

                # thread end check
                if self._stop_event.is_set():
                    print("Process thread stopped.")
                    return
    
                # MOVE DONE FILES if requested
                if self._config["settings"]["move_done_files"] == "true":
                    self._comm.send_to_print("   - moving the file...")
                    self._utils.move_done_file(file, self._config["settings"]["mf4_path"], self._config["settings"]["done_path"])

                num_of_done_mf4_files += 1
                self._comm.send_command(f"PROG#{round((num_of_done_mf4_files / num_of_mf4_files), 2)}")
                self._comm.send_to_print(f"   - DONE!     Overall progress:  {round((num_of_done_mf4_files / num_of_mf4_files)*100, 2)} %")
                self._comm.send_to_print()

        except Exception as e:
            self._comm.send_error("ERROR", f"Process error:\n{e}", "T")
            return

        self._comm.send_to_print()
        self._comm.send_to_print("                                      ~ ")           
        self._comm.send_to_print("Everything completed successfully!  c[_]")
        self._comm.send_to_print()
        self._comm.send_command("FINISH")
        return
