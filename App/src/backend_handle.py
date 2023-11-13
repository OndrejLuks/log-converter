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
        self._stop_event = threading.Event()

        self._comm = PipeCommunication(connection, self._stop_event)
        self._utils = Utils(self._comm)
        

        self._config = self._utils.open_config("src/config.json")
        self._db = DatabaseHandle(self._config, self._comm, self._stop_event)

        self._threads = []

        self._conv = Conversion(self._utils, self._comm, self._db, self._stop_event, self._threads, self._config)


    def run(self):
        while True:
            event = self._comm.receive()

            match event:
                case "RUN-PROP":
                    self._conv.check_db_override()

                case "RUN-ACK":
                    thr_proc = threading.Thread(target=self._conv.process_handle)
                    thr_proc.start()
                    self._threads.append(thr_proc)

                case "U-CONF":
                    self._update_configs()
                
                case "END":
                    self._thread_cleanup()
                    break

                case _:
                    self._comm.send_to_print("Unknown command to the process")
        
        self._comm.send_command("END")
        return
    

    def _thread_cleanup(self) -> None:
        # stop all threads
        self._stop_event.set()

        # join all threads
        for thr in self._threads:
            if thr.is_alive():
                thr.join()

        return
    

    def _update_configs(self) -> None:
        self._config = self._utils.open_config("src/config.json")
        self._db.update_config(self.config)
        self._conv.update_config(self.config)
        self._comm.send_to_print("Settings updated.")

        return
