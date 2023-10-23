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
from src import procData, mfd, myDB, gui, utils
from pathlib import Path
import pandas as pd
import os
import json
import warnings
import threading
import can_decoder
import canedge_browser


# ==========================================================================================================================
# ==========================================================================================================================


class Process():
    def __init__(self, gui_interface: gui.AppInterface, utilities: utils.Utils):
        self.gui_interface = gui_interface
        self.utils = utilities
        self.config = None
        self.dbc_list = self.create_dbc_list()

        self.gui_interface.set_start_function(self.safe_run_process_handle)

# -----------------------------------------------------------------------------------------------------------

    def run(self) -> None:
        self.gui_interface.run()
        return

# -----------------------------------------------------------------------------------------------------------    

    def open_config(self):
        """Loads configure json file (config.json) from root directory. Returns json object."""
        self.gui_interface.print_to_box("Reading config file ...  ")

        try:
            with open(os.path.join("src", "config.json"), "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            self.gui_interface.print_to_box()
            self.gui_interface.print_to_box("ERROR while reading src\config.json file. Check for file existance.\n")
            self.gui_interface.exit()

        self.gui_interface.print_to_box("done!\n")
        return data
    
# -----------------------------------------------------------------------------------------------------------

    def create_dbc_list(self) -> list:
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
            self.gui_interface.print_to_box()
            self.gui_interface.print_to_box("ERROR while loading DBC files. Check for file existance.\n")
            self.gui_interface.exit()

        return db_list

# -----------------------------------------------------------------------------------------------------------

    def setup_fs(self) -> canedge_browser.LocalFileSystem:
        """Sets up a filesystem required for signal extraxtion from raw MF4"""
        base_path = Path(__file__).parent
        return canedge_browser.LocalFileSystem(base_path=base_path)

# -----------------------------------------------------------------------------------------------------------

    def convert_mf4(self, mf4_file: os.path) -> list:
        """Converts and decodes MF4 files to a dataframe using DBC files."""
        fs = self.setup_fs()
        proc = procData.ProcessData(fs, self.dbc_list)

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
        if self.config["settings"]["write_time_info"]:
            self.gui_interface.print_to_box("   - writing time information into MF4-info.csv... \n")
            # check if df is not empty
            if df_phys.shape[0] > 0:
                self.utils.write_time_info(mf4_file, df_phys.index[0], df_phys.index[-1])

        self.gui_interface.print_to_box("   - extracting individual signals... \n")
        return self.split_df_by_cols(df_phys)

# -----------------------------------------------------------------------------------------------------------

    def aggregate(self, df, lock: threading.Lock, dfs: list) -> None:
        """Aggregates input signal dataframe by removing redundant values"""
        num_rows = df.shape[0]

        if num_rows > 0:
            sig_name = df.columns.values[0]
            with lock:
                self.gui_interface.print_to_box(f"     > started aggregating signal: {sig_name}\n")
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
                elif (time_diff > timedelta(seconds=self.config["settings"]["agg_max_skip_seconds"])):
                    idx_array.append(idx)
                    previous = idx

            # add last item into the mask
            idx_array.append(num_rows - 1)
            # create a new dataframe and remove duplicates
            result_df = df.iloc[list(dict.fromkeys(idx_array))]
            
            # safely store the aggregated signal
            with lock:
                dfs.append(result_df)
                self.gui_interface.print_to_box(f"     = finished agg. signal: {sig_name}\n")

# -----------------------------------------------------------------------------------------------------------                

    def split_df_by_cols(self, df) -> list:
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
    
    def safe_run_process_handle(self) -> None:
        # load config
        self.config = self.open_config()
        
        # check DB override
        if self.config["settings"]["clean_upload"]:
            type = "WARNING!"
            msg = 'With "Clean upload" enabled, the whole current database will be erased!'
            ques = "Do you really want to proceed?"
            self.gui_interface.generate_pop_up_yn(type, msg, ques, lambda: self.gui_interface.callback_w_toplevel_kill(self.run_process_handle), self.gui_interface.kill_pop_up)
        
        else:
            # run the process
            self.run_process_handle()

        return

# -----------------------------------------------------------------------------------------------------------

    def run_process_handle(self) -> None:
        thread = threading.Thread(target=self.process_handle)
        thread.start()

        return

# -----------------------------------------------------------------------------------------------------------

    def process_handle(self) -> None:
        """Function that handles MF4 files process from conversion to upload"""
        self.gui_interface.disable_buttons()
        self.gui_interface.show_progress_bar()

        # prepare the database
        db = myDB.DatabaseHandle(self.config, self.gui_interface)
        db.connect()
        db.create_schema()        

        # load MF4 files
        mf4_file_list, num_of_mf4_files = self.utils.get_MF4_files("SourceMF4")
        num_of_done_mf4_files = 0

        try: 
            for file in mf4_file_list:
                # CONVERT FILE into Signal files
                self.gui_interface.print_to_box(f" - Converting: {file}\n")
            
                dfs_to_upload = []
                converted_files = self.convert_mf4(file)

                # AGGREGATE if requested
                if self.config["settings"]["aggregate"]:
                    threads = []
                    self.gui_interface.print_to_box("   - aggregating... \n")
                    # run each signal in a different thread
                    lock = Lock()
                    for signal_df in converted_files:
                        thread = threading.Thread(target=self.aggregate, args=(signal_df, lock, dfs_to_upload))
                        threads.append(thread)
                        thread.start()
                    
                    # wait for threads to finish
                    for thr in threads:
                        thr.join()
                
                else:
                    dfs_to_upload = converted_files

                # UPLOAD TO DB
                self.gui_interface.print_to_box("   - uploading... \n")
                db.upload_data(dfs_to_upload)
    
                # MOVE DONE FILES if requested
                if self.config["settings"]["move_done_files"]:
                    self.gui_interface.print_to_box("   - moving the file... \n")
                    self.utils.move_done_file(file, "SourceMF4")

                num_of_done_mf4_files += 1
                self.gui_interface.print_to_box(f"   - DONE!     Overall progress:  {round((num_of_done_mf4_files / num_of_mf4_files)*100, 2)} %\n")
                self.gui_interface.update_progress_bar(round((num_of_done_mf4_files / num_of_mf4_files), 2))
                self.gui_interface.print_to_box()

        except Exception as e:
            self.gui_interface.print_to_box()
            self.gui_interface.enable_buttons()
            self.gui_interface.print_to_box(f"Process ERROR:  {e}\n")
            self.gui_interface.exit()

        self.gui_interface.enable_buttons()
        self.gui_interface.hide_progress_bar()

        self.gui_interface.print_to_box()
        self.gui_interface.print_to_box("                                      ~ \n")           
        self.gui_interface.print_to_box("Everything completed successfully!  c[_]\n")
        self.gui_interface.print_to_box()
        return

# ==========================================================================================================================

def warning_handler(message, category, filename, lineo, file=None, line=None) -> None:
    """Handles warnings for more compact vizualization. Mostly only because of blank signal convertion."""
    return

# ==========================================================================================================================

def main():
    warnings.showwarning = warning_handler

    app_gui = gui.App()
    app_interface = gui.AppInterface(app_gui)
    app_utilities = utils.Utils(app_interface)

    app = Process(app_interface, app_utilities)
    app.run()

# ==========================================================================================================================

if __name__ == '__main__':
    main()