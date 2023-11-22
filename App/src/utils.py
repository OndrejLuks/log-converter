# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ==========================================================================================================================
# ==========================================================================================================================


from .communication import PipeCommunication
from datetime import datetime
import os
import pytz
import json
import shutil



# ==========================================================================================================================
# ==========================================================================================================================


class Utils():
    """Utility function mainly for the Process class.
    
    Attributes
    ----------
    - gui_interface
        - reference to an instance of the AppInterface class
        - required upon construction
        
    Methods
    -------
    - write_time_into (file, start_time, end_time)
    - get_MF4_files (top_level)
    - rm_empty_subdirs (top_level)
    - move_done_file (file, source_top_level)
    - create_dir (target_dir)
    """

    def __init__(self, communication: PipeCommunication) -> None:
        self._comm = communication

# --------------------------------------------------------------------------------------------------------------------------------
    
    def write_time_info(self, file: str, start_time, end_time) -> None:
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
            self._comm.send_error("WARNING", f"Failed to write MF4 info:\n{e}", "F")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def get_MF4_files(self, top_level: str) -> list:
        """Generates a list of paths to all found MF4 files in the SourceMF4 folder. Returns also the number of found files."""
        out = []
        try:
            # search for MF4 files
            for root, dirs, files in os.walk(top_level):
                # mostly "files" consists of only 1 file
                for file in files:
                    if file.endswith(".MF4"):
                        # found MF4 file
                        mf4_file = os.path.join("..", root, file)
                        out.append(mf4_file)

        except Exception as e:
            self._comm.send_error("ERROR", f"Error while reading MF4 files:\n{e}", "T")
            out.clear()

        if len(out) == 0:
            self._comm.send_to_print()
            self._comm.send_to_print("WARNING: No MF4 files found!\n")
            self._comm.send_to_print()

        return out, len(out)

# --------------------------------------------------------------------------------------------------------------------------------

    def rm_empty_subdirs(self, top_level: str) -> None:
        """Removes empty directories in given root"""
        try:
            for root, dirs, files in os.walk(top_level, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)

        except OSError:
            self._comm.send_error("WARNING", f"Failed to remove empty subdirs of root {top_level}", "F")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def move_done_file(self, file: os.path, source_top_level) -> None:
        """Moves given file from SourceMF4 folder to DoneMF4 folder"""
        # get target file path
        target_file = file.replace(source_top_level, "DoneMF4")
        # get and create target directory
        target_dir = os.path.dirname(target_file)
        self.create_dir(target_dir)

        try:
            # move the file
            shutil.move(file, target_file)

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with file movement:\n{e}", "F")

        # remove empty source folders
        self.rm_empty_subdirs("SourceMF4")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def create_dir(self, target_dir: str) -> None:
        """Creates given directory if it doesn't exist"""
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with dir creation:\n{e}", "F")
        
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def open_config(self, path: str):
        """Loads configure json file (config.json) from root directory. Returns json object."""

        try:
            with open(path, "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            print()
            print(f"ERROR while reading {path} file. Check for file existance.")
            return None

        return data
    
# --------------------------------------------------------------------------------------------------------------------------------

    def time_valid(self, date_time: str) -> bool:
        # date_time comes in format: "yyy-mm-dd hh:mm:ss"
        try:
            time_list = date_time.split(" ")[1].split(":")
            
            try:
                hh = int(time_list[0])
                mm = int(time_list[1])
                ss = int(time_list[2])

            except ValueError:
                return False
            
            if hh < 0 or hh > 23:
                return False
            
            if mm < 0 or mm > 59:
                return False
            
            if ss < 0 or ss > 59:
                return False
            
        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with time validation:\n{e}", "F")
            return False
        
        return True

# --------------------------------------------------------------------------------------------------------------------------------

    def time_date_follow_check(self, sooner: str, later: str) -> bool:
        try:
            from_dt = datetime.strptime(sooner, "%Y-%m-%d %H:%M:%S")
            to_dt = datetime.strptime(later, "%Y-%m-%d %H:%M:%S")

            if from_dt > to_dt:
                return False
            
        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with time date validation:\n{e}", "F")
            return False
            
        return True
