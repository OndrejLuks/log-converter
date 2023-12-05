# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from .communication import PipeCommunication
from .utils import Utils
from .conversion import Conversion
from .db_handle import DatabaseHandle
import threading

# ================================================================================================================================
# ================================================================================================================================


class BackendHandle():
    def __init__(self, connection):
        self._threads = []
        self._fault = False
        self._stop_event = threading.Event()

        self._comm = PipeCommunication(connection, self._stop_event)
        self._utils = Utils(self._comm)
        

        self._config = self._utils.open_config("src/config.json")
        if self._config == None:
            self._fault = True
            return

        self._db = DatabaseHandle(self._config, self._comm, self._stop_event)
        self._conv = Conversion(self._utils, self._comm, self._db, self._stop_event, self._threads, self._config)

# --------------------------------------------------------------------------------------------------------------------------------

    def run(self):
        # initialize GUI frames 
        if not self._fault:
            self._comm.send_command("INIT")
        
        while True:
            try:
                event = self._comm.receive()

                # tokenize the message by '#'
                messages = event.split("#")

                match messages[0]:
                    case "RUN-PROP":
                        self._conv.check_db_override()

                    case "RUN-ACK":
                        thr_proc = threading.Thread(target=self._conv.process_handle)
                        thr_proc.start()
                        self._threads.append(thr_proc)

                    case "U-CONF":
                        if len(messages) == 4:
                            self._update_config_value(messages[1], messages[2], messages[3])
                        else:
                            self._comm.send_error("WARNING", "Blank config update requested!", False)

                    case "FETCH-CONF":
                        if len(messages) == 3:
                            self._fetch_conf_value(messages[1], messages[2])
                        else:
                            self._comm.send_error("WARNING", "Blank config fetch requested!", False)

                    case "FLUSH-CONF":
                        self._utils.flush_config("src/config.json", self._config)
                        self._update_configs()

                    case "FETCH-SIG":
                        self._fetch_signals()

                    case "DOWNL":
                        if len(messages) == 5:
                            self._download_signal(sigs=messages[1], from_str=messages[2], to_str=messages[3], file_name=messages[4])
                        else:
                            self._comm.send_error("WARNING", "Blank download requested!", False)

                    case "END":
                        self._thread_cleanup()
                        break

                    case _:
                        self._comm.send_to_print("Unknown command to the process")

            except Exception as e:
                self._comm.send_error("ERROR", f"Problem in main backend loop:\n{e}", "T")
    
        self._comm.send_command("END")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _thread_cleanup(self) -> None:
        # stop all threads
        self._stop_event.set()

        # join all threads
        for thr in self._threads:
            if thr.is_alive():
                thr.join()

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _update_configs(self) -> None:
        self._config = self._utils.open_config("src/config.json")
        self._db.update_config(self._config)
        self._conv.update_config(self._config)
        self._comm.send_to_print("Settings updated.")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _update_config_value(self, domain: str, field: str, content: str) -> None:
        try:
            self._config[domain][field] = str(content)

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with updating local settings:\n{e}", "F")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _fetch_conf_value(self, domain: str, field: str) -> None:
        try:
            value = str(self._config[domain][field])
            self._comm.send_command(f"C-VAL#{value}")

        except Exception as e:
            self._comm.send_error("WARNING", f"Problem with fetching local settings:\n{e}", "F")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _fetch_signals(self) -> None:
        self._db.connect()
        tbl_names = self._db.get_table_names()
        self._db.finish()

        if not tbl_names == None:
            if len(tbl_names) == 0:
                self._comm.send_error("WARNING", "No signals found!", "F")
                return
            
            self._comm.send_command("U-SIG")
            
            for tbl in tbl_names:
                self._comm.send_command(tbl)

            self._comm.send_command("U-SIG-END")
        
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _download_signal(self, sigs: str, from_str: str, to_str: str, file_name: str) -> None:

        if not (self._utils.time_valid(from_str) and self._utils.time_valid(to_str)):
            self._comm.send_error("WARNING", "Entered time values are not real.", "F")
            return
        
        if not self._utils.time_date_follow_check(from_str, to_str):
            self._comm.send_error("WARNING", "FROM time is set after TO time.", "F")
            return

        self._threads.append(self._utils.spawn_working_thread(fc=self._db.save_data, args=(sigs, from_str, to_str, file_name)))
        return
