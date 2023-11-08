# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ==========================================================================================================================
# ==========================================================================================================================


class PipeCommunication():
    def __init__(self, conn, event):
        self.pipe = conn
        self.stop_event = event

# -----------------------------------------------------------------------------------------------------------

    def send_to_print(self, message='', end='\n') -> None:
        if not self.stop_event.is_set():
            self.pipe.send(f"PRINT#{message}{end}")
        return

# -----------------------------------------------------------------------------------------------------------    

    def send_command(self, command) -> None:
        self.pipe.send(command)
        return
    
# -----------------------------------------------------------------------------------------------------------    

    def send_error(self, type: str, message: str, terminate: str) -> None:
        self.pipe.send(f"POP-ERR#{type}#{message}#{terminate}")
        return
    
# ----------------------------------------------------------------------------------------------------------- 

    def receive(self) -> str:
        return self.pipe.recv()
