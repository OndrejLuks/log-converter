# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from . import communication, Conversion, utils, myDB
import threading


# ================================================================================================================================
# ================================================================================================================================


class BackendHandle():
    def __init__(self, connection):
        self.stop_event = threading.Event()

        self.comm = communication.PipeCommunication(connection, self.stop_event)
        self.utils = utils.Utils(self.comm)
        

        self.config = self.utils.open_config("src/config.json")
        self.db = myDB.DatabaseHandle(self.config, self.comm, self.stop_event)

        self.threads = []

        self.conv = Conversion.Conversion(self.utils, self.comm, self.db, self.stop_event, self.threads, self.config)


    def run(self):
        while True:
            event = self.comm.receive()

            match event:
                case "RUN-PROP":
                    self.conv.check_db_override()

                case "RUN-ACK":
                    thr_proc = threading.Thread(target=self.conv.process_handle)
                    thr_proc.start()
                    self.threads.append(thr_proc)

                case "END":
                    self.thread_cleanup()
                    break

                case _:
                    self.comm.send_to_print("Unknown command to the process")
        
        self.comm.send_command("END")
        return
    

    def thread_cleanup(self) -> None:
        # stop all threads
        self.stop_event.set()

        # join all threads
        for thr in self.threads:
            if thr.is_alive():
                thr.join()

        return
