# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================


class PipeCommunication():
    def __init__(self, conn, event):
        self._pipe = conn
        self._stop_event = event

# --------------------------------------------------------------------------------------------------------------------------------

    def send_to_print(self, message='', end='\n') -> None:
        if self._stop_event == None:
            self._pipe.send(f"PRINT#{message}{end}")
            return
        
        if not self._stop_event.is_set():
            self._pipe.send(f"PRINT#{message}{end}")

        return

# --------------------------------------------------------------------------------------------------------------------------------  

    def send_command(self, command) -> None:
        self._pipe.send(command)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------  

    def send_error(self, type: str, message: str, terminate: str) -> None:
        self._pipe.send(f"POP-ERR#{type}#{message}#{terminate}")
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def receive(self) -> str:
        return self._pipe.recv()
