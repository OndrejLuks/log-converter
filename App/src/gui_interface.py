# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com

# ================================================================================================================================
# ================================================================================================================================

from .gui import App
from .communication import PipeCommunication
import threading

# ================================================================================================================================
# ================================================================================================================================


class AppInterface():
    """Interface for the App class.
    
    Attributes
    ----------
    - app
        - reference to an instance of the App class
        - required upon construction
        
    Methods
    -------
    - generate_pop_up_yn (type, message, question, callback_yes, callback_no)
    - generate_pop_up_ok (type, message)
    - kill_pop_up ()
    - print_to_box (message)
    - save_changes ()
    - disable_buttons ()
    - enable_buttons ()
    - show_progress_bar ()
    - hide_progress_bar ()
    - update_progress_bar ()
    """

    def __init__(self, app: App, pipe):
        """Constructior of AppInterface"""
        self.app = app
        self.thr_event = threading.Event()
        self.comm = PipeCommunication(pipe, None)
        self.app.set_communication(self.comm)
        self.app.thr_event = self.thr_event

# --------------------------------------------------------------------------------------------------------------------------------
    
    def run(self) -> None:
        """Runs and shows the GUI application
        
        Returns
        -------
        None
        """

        try:
            # create a new thread with function that will read from PIPE
            read_thr = threading.Thread(target=self.read_pipe)
            read_thr.start()

            # update GUI - blocking function
            self.app.mainloop()

            read_thr.join()

        except Exception as e:
            print(f"Error occured in the main GUI run() method:\n{e}")

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def read_pipe(self) -> None:
        while True:
            event = self.comm.receive()

            # tolekize the message by '#'
            messages = event.split("#")

            match messages[0]:
                case "INIT":
                    init_thr = threading.Thread(target=self.app.init)
                    init_thr.start()

                case "FINISH":
                    self.enable_buttons()
                    self.hide_progress_bar()
                
                case "START":
                    self.disable_buttons()
                    self.show_progress_bar()
                    
                case "PRINT":
                    if len(messages) == 2:
                        self.print_to_box(messages[1])
                    else:
                        self.generate_pop_up_error("WARNING", "Blank message print requested!", False)

                case "CLS":
                    self.clear_textbox()

                case "PROG":
                    if len(messages) == 2:
                        self.update_progress_bar(float(messages[1]))
                    else:
                        self.generate_pop_up_error("WARNING", "Blank progress update requested!", False)

                case "POP-ACK":
                        if len(messages) == 4:
                            self.generate_pop_up_yn(messages[1], messages[2], messages[3], self.send_ack, self.kill_pop_up)
                        else:
                            self.generate_pop_up_error("WARNING", "Requested ack popup with wrong number of parameters!", False)

                case "POP-ERR":
                    if len(messages) == 4:
                        self.generate_pop_up_error(messages[1], messages[2], messages[3] == "T")
                    else:
                        self.generate_pop_up_error("WARNING", "Requested error popup with wrong number of parameters!", False)

                case "U-SIG":
                    self.update_signals()

                case "C-VAL":
                    if len(messages) == 2:
                        self.set_conf_value(messages[1])
                    else:
                        self.generate_pop_up_error("WARNING", "Blank config value update requested!", False)

                case "ACK":
                    self.send_ack()

                case "TERMINATE":
                    self.app.kill_main_window()
                    break

                case "END":
                    break

                case _:
                    self.generate_pop_up_error("WARNING", f"Can't recognize received item: {messages}", False)

        self.app.kill_main_window()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_signals(self) -> None:
        new_signals = []
        
        while(True):
            sig = self.comm.receive()

            if sig == "U-SIG-END":
                break

            new_signals.append(sig)

        # sort alphabetically
        new_signals.sort()
        # update signals in gui
        self.app.download_frame.update_signals(new_signals)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def send_ack(self) -> None:
        self.comm.send_command("RUN-ACK")
        self.kill_pop_up()
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def generate_pop_up_yn(self, type: str, message: str, question: str, callback_yes: callable, callback_no: callable) -> None:
        """Generates a desired popup window with YES and NO buttons.
        
        Parametres
        ----------
        - type : str
            - Name of the window
        - message : str
            - Displayed message in the white box
        - question : str
            - Displayed question under the message
        - callback_yes
            - Function assigned to the YES button
        - callback_no
            - Function assigned to the NO button
            
        Returns
        -------
        None
        """
        self.app.open_toplevel_yn(type, message, question, callback_yes, callback_no)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------    

    def generate_pop_up_error(self, type: str, message: str, terminate: bool) -> None:
        self.app.error_handle(type, message, terminate)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def kill_pop_up(self) -> None:
        """Closes the currently open toplevel pop-up"""
        self.app.kill_toplevel()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def set_conf_value(self, val: str) -> None:
        self.app.curr_conf_val = val
        self.thr_event.set()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def print_to_box(self, message: str = '\n') -> None:
        """Prints the given message into the GUI textbox.
        
        Parametres
        ----------
        - message : str
            - Message to be printed
        
        Returns
        -------
        None"""
        
        self.app.text_box.write(message)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def clear_textbox(self) -> None:
        self.app.text_box.clear()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def disable_buttons(self) -> None:
        """Disables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.disable_buttons()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def enable_buttons(self) -> None:
        """Enables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.enable_buttons()
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def show_progress_bar(self) -> None:
        """Shows the progress bar under the textbox.
        
        Returns
        -------
        None"""

        self.app.progress_bar.show()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def hide_progress_bar(self) -> None:
        """Hides the progress bar under the textbox.
        
        Returns
        -------
        None"""  

        self.app.progress_bar.hide()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_progress_bar(self, value: float) -> None:
        """Updates the progress bar to the given value.
        
        Parametres
        ----------
        - value
            - float value of progress, between 0 and 1
            
        Returns
        -------
        None"""

        self.app.progress_bar.set_value(value)
        return
