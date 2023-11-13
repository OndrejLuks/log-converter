# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================


import customtkinter
import threading
import json
import time
import os


# ==========================================================================================================================
# ==========================================================================================================================


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

    def __init__(self, app, pipe):
        """Constructior of AppInterface"""
        self.app = app
        self.pipe = pipe

        self.app.set_connection(pipe)

# -----------------------------------------------------------------------------------------------------------
    
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
            print(f"Error occured in the main run() method:\n{e}")

        return

# -----------------------------------------------------------------------------------------------------------

    def read_pipe(self) -> None:
        while True:
            event = self.pipe.recv()

            # tolekize the message by '#'
            messages = event.split("#")

            match messages[0]:
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

                case "ACK":
                    self.send_ack()

                case "END":
                    break

                case _:
                    self.generate_pop_up_error("WARNING", f"Can't recognize received item: {messages}", False)

        self.app.kill_main_window()
        return


# -----------------------------------------------------------------------------------------------------------

    def send_ack(self) -> None:
        self.pipe.send("RUN-ACK")
        self.kill_pop_up()
        return

# -----------------------------------------------------------------------------------------------------------
    
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
    
# -----------------------------------------------------------------------------------------------------------    

    def generate_pop_up_error(self, type: str, message: str, terminate: bool) -> None:
        self.app.error_handle(type, message, terminate)
        return
    
# -----------------------------------------------------------------------------------------------------------

    def kill_pop_up(self) -> None:
        """Closes the currently open toplevel pop-up"""
        self.app.kill_toplevel()
        return

# -----------------------------------------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------------------------------------

    def disable_buttons(self) -> None:
        """Disables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.disable_buttons()
        return

# -----------------------------------------------------------------------------------------------------------

    def enable_buttons(self) -> None:
        """Enables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.enable_buttons()
        return

# -----------------------------------------------------------------------------------------------------------
    
    def show_progress_bar(self) -> None:
        """Shows the progress bar under the textbox.
        
        Returns
        -------
        None"""

        self.app.progress_bar.show()
        return

# -----------------------------------------------------------------------------------------------------------

    def hide_progress_bar(self) -> None:
        """Hides the progress bar under the textbox.
        
        Returns
        -------
        None"""  

        self.app.progress_bar.hide()
        return

# -----------------------------------------------------------------------------------------------------------

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
    
        
# ================================================================================================================================

class TopWindowYesNo(customtkinter.CTkToplevel):
    """Class representing a yes/no pop-up window.
    
    Child of customtkinter.CTkToplevel.
    
    Attributes
    ----------
    - msg : customtkinter.CTkLabel
    - question : customtkinter.CTkLabel
    - btn_yes : customtkinter.CTkButton
    - btn_no : customtkinter.CTkButton
    """

    def __init__(self, master, type: str, msg: str, question: str, btn_callback_yes=None, btn_callback_no=None):
        super().__init__(master)

        try:
            self.minsize(300, 150)
            self.resizable(False, False)
            self.title(type)
            self.configure(fg_color=self.master.col_popup_yn_bg)

            self.grid_columnconfigure((0, 1), weight=1)
            
            # bring the window into the foregroud
            self.after(100, self.lift)

            # Message
            self._msg = customtkinter.CTkLabel(self, text=msg, fg_color=self.master.col_popup_yn_lab, text_color=self.master.col_popup_yn_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 0), sticky="nswe")

            # Question
            self._question = customtkinter.CTkLabel(self, text=question, text_color=self.master.col_popup_yn_tx)
            self._question.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nswe")

            # YES button
            self._btn_yes = customtkinter.CTkButton(self, text="Yes", text_color=self.master.col_btn_tx, command=btn_callback_yes)
            self._btn_yes.grid(row=2, column=0, padx=10, pady=10, sticky="nswe")

            # NO button
            self._btn_no = customtkinter.CTkButton(self, text="No", text_color=self.master.col_btn_tx, command=btn_callback_no)
            self._btn_no.grid(row=2, column=1, padx=10, pady=10, sticky="nswe")
        
        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")
        
# ================================================================================================================================

class TopWindowOk(customtkinter.CTkToplevel):
    """Class representing a warning pop-up window.
    
    Child of customtkinter.CTkToplevel.
    
    Attributes
    ----------
    - msg : customtkinter.CTkLabel
    - question : customtkinter.CTkLabel
    - btn_ok : customtkinter.CTkButton

    Methods
    -------
    - close()
    """

    def __init__(self, master, type: str, msg: str, callback: callable = None):
        super().__init__(master)

        try:
            self.minsize(300, 120)
            self.resizable(False, False)
            self.title(type)
            self.configure(fg_color=self.master.col_popup_ok_bg)
            self.grid_columnconfigure(0, weight=1)
        
            # bring the window into the foregroud
            self.after(100, self.lift)

            # Message
            self._msg = customtkinter.CTkLabel(self, text=msg, fg_color=self.master.col_popup_ok_lab, text_color=self.master.col_popup_ok_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="nswe")

            # OK button
            self._btn_ok = customtkinter.CTkButton(self, text="Okay", text_color=self.master.col_btn_tx, command=callback)
            self._btn_ok.grid(row=1, column=0, padx=10, pady=10, sticky="swe")
        
        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

        return
        
# ================================================================================================================================         

class TopWindowExit(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        try:
            self.minsize(300, 100)
            self.resizable(False, False)
            self.title("Information")
            self.grid_columnconfigure(0, weight=1)
        
            # bring the window into the foregroud
            self.after(100, self.lift)

            msg = "Application is closing..."

            # Message
            self._msg = customtkinter.CTkLabel(self, text=msg, fg_color=self.master.col_popup_ok_lab, text_color=self.master.col_popup_ok_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="nswe")
        
        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")


# ================================================================================================================================   


class DatabaseFrame(customtkinter.CTkFrame):
    """Class representing the frame for database settings.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - title : customtkinter.CTkLabel
    - entries : customtkinter.CTkEntry []
    - labels : customtkinter.CTkLabel []
        
    Methods
    -------
    - refresh()
    - save_to_json()
    """

    def __init__(self, master):
        super().__init__(master)

        try:

            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=2)
            
            # Frame title
            self.title = customtkinter.CTkLabel(self, text="Database configuration", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
            
            # define entry names
            self.entry_names = [("Host", "host"),
                        ("Port", "port"),
                        ("Database", "database"),
                        ("User", "user"),
                        ("Password", "password"),
                        ("Schema", "schema_name")]
            self._entries = []
            self._labels = []

            # create entries
            for i, name in enumerate(self.entry_names):
                label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
                label.grid(row=i+1, column=0, padx=15, pady=10, sticky="w")
                entry = customtkinter.CTkEntry(self, placeholder_text=self.master.my_config["database"][name[1]])
                entry.grid(row=i+1, column=1, padx=10, pady=10, sticky="we")

                self._labels.append(label)
                self._entries.append((entry, name[1]))

        except Exception:
            self.master.error_handle("ERROR", "Unable to create GUI - database", terminate=True)



    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.my_config["database"][entry[1]])

        return

    
    def save_to_json(self) -> bool:
        """Saves database settings changes into the config.json file"""
        try:
            # update config
            for entry in self._entries:
                val = str(entry[0].get())
                if not len(val) == 0:
                    self.master.my_config["database"][entry[1]] = val

            # write to the file:
            with open(os.path.join("src", "config.json"), "w") as file:
                json.dump(self.master.my_config, file, indent=4)

        except Exception:
            self.master.error_handle("WARNING", "Unable to save the settings", terminate=False)
            return False

        return True        

# ================================================================================================================================   

class ProcessFrame(customtkinter.CTkFrame):
    """Class representing the frame for process settings.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - title : customtkinter.CTkLabel
    - switches : customtkinter.CTkSwitch []
    - entries : customtkinter.CTkEntry []
    - labels : customtkinter.CTkLabel []
        
    Methods
    -------
    - refresh()
    - save_to_json()
    """
    
    def __init__(self, master):
        super().__init__(master)

        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=2)

            # Frame title
            self._title = customtkinter.CTkLabel(self, text="Process configuration", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")

            # define switch names
            switch_names = [("Aggregate", "aggregate"),
                            ("Move done files", "move_done_files"),
                            ("Write time info", "write_time_info"),
                            ("Clean upload", "clean_upload")]
            self._switches = []

            # create switches
            for i, name in enumerate(switch_names):
                switch = customtkinter.CTkSwitch(self, text=name[0])
                switch.grid(row=i+1, column=0, columnspan=2, padx=10, pady=10, sticky="w")

                # set default switch position
                if self.master.my_config["settings"][name[1]]:
                    switch.select()

                self._switches.append((switch, name[1]))

            # define entry names
            entry_names = [("Agg. max skip seconds", "agg_max_skip_seconds")]
            self._entries = []
            self._labels = []
            # create entries
            for i, name in enumerate(entry_names):
                label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
                label.grid(row=i+1+len(self._switches), column=0, padx=10, pady=10, sticky="w")
                entry = customtkinter.CTkEntry(self, placeholder_text=self.master.my_config["settings"][name[1]])
                entry.grid(row=i+1+len(self._switches), column=1, padx=10, pady=10, sticky="we")

                self._labels.append(label)
                self._entries.append((entry, name[1]))
        
        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - process\n{e}", terminate=True)

    
    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.my_config["settings"][entry[1]])

        return


    def save_to_json(self) -> bool:
        """Saves process settings changes into the config.json file"""
        # update config
        for switch in self._switches:
            val = int(switch[0].get())
            if val == 1:
                self.master.my_config["settings"][switch[1]] = True
            if val == 0:
                self.master.my_config["settings"][switch[1]] = False

        for entry in self._entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                # try to convert numbers from entries into string
                try:
                    val = int(val)

                except ValueError:
                    self.master.error_handle("WARNING", f'"{val}" is not a number!', terminate=False)
                    return False
                
                # save
                self.master.my_config["settings"][entry[1]] = val

        # write to the file:
        try:
            with open(os.path.join("src", "config.json"), "w") as file:
                json.dump(self.master.my_config, file, indent=4)
        
        except Exception:
            self.master.error_handle("WARNING", "Unable to save the settings", terminate=False)
            return False
        
        return True

# ================================================================================================================================

class TextboxFrame(customtkinter.CTkFrame):
    """Class representing the frame for textbox.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - title : customtkinter.CTkLabel
    - textbox : customtkinter.CTkTextbox
        
    Methods
    -------
    - write(msg)
    """

    def __init__(self, master):
        super().__init__(master)

        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)

            # frame title
            self._title = customtkinter.CTkLabel(self, text="Feedback prompt", fg_color="transparent")
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="we")
            
            # define textbox
            self._textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, activate_scrollbars=True, wrap="word")
            self._textbox.grid(row=1, column=0, sticky="nsew")
            self._textbox.configure(state="disabled", font=("Courier New", 12))

        except Exception:
            self.master.error_handle("ERROR", "Unable to create GUI - textbox", terminate=True)


    def write(self, msg: str = "\n") -> None:
        """Prints the given message to the GUI's textbox.
        
        Parameters
        ----------
        - msg : str
            - message to be printed
        """
        # make the textbox writeable
        self._textbox.configure(state="normal")
        # insert message at the end
        self._textbox.insert("end", msg)
        # scroll to the end
        self._textbox.see("end")
        # make the textbox non-writeable
        self._textbox.configure(state="disabled")
        return

# ================================================================================================================================

class ProgressFrame(customtkinter.CTkFrame):
    """Class representing the frame for progress bar.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - title : customtkinter.CTkLabel
    - progress : customtkinter.CTkProgressBar
        
    Methods
    -------
    - show()
    - hide()
    - set_value()
    """

    def __init__(self, master):
        super().__init__(master)

        try:
            self.configure(fg_color="transparent", height=15)
            self.grid_columnconfigure(1, weight=1)

            # frame title
            self._title = customtkinter.CTkLabel(self, text="Progress", fg_color="transparent", height=1)
            self._title.grid_forget()
            
            # define progress bar
            self._progress = customtkinter.CTkProgressBar(master=self, mode="determinate", corner_radius=0, fg_color=self.master.col_progress_bg, progress_color=self.master.col_progress_bar, height=1)
            self._progress.set(0)
            self._progress.grid_forget()

        except Exception:
            self.master.error_handle("ERROR", "Unable to create GUI - progress", terminate=True)


    def show(self) -> None:
        """Shows this object inside the master window."""
        try:
            self._title.grid(row=0, column=0, padx=10, pady=0, sticky="w")
            self._progress.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")

        except Exception:
            self.master.error_handle("WARNING", "Unable to show the progress frame", terminate=False)

        return


    def hide(self) -> None:
        """Hides this object within the master window."""
        try:
            self._title.grid_forget()
            self._progress.grid_forget()

        except Exception:
            self.master.error_handle("WARNING", "Unable to hide the progress frame", terminate=False)

        return


    def set_value(self, val: float) -> None:
        """Sets given value to the progress bar.

        Parameters
        ----------
        - val : float
            - only numbers from closed interval <0 to 1>
        """
        try:
            self._progress.set(val)

        except Exception:
            self.master.error_handle("WARNING", "Unable set a new value of the progress frame", terminate=False)

        return

# ================================================================================================================================

class ButtonsFrame(customtkinter.CTkFrame):
    """Class representing the frame for buttons.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - btn_discard : customtkinter.CTkButton
    - btn_start : customtkinter.CTkButton
    - btn_save : customtkinter.CTkButton
    - btn_save_start : customtkinter.CTkButton
        
    Methods
    -------
    - btn_callback_discard()
    - btn_callback_start()
    - btn_callback_save_start()
    - disable_buttons()
    - enable_buttons()
    - exit_program()
    """

    def __init__(self, master):
        super().__init__(master)
        
        try:
            self.grid_columnconfigure((0, 1, 2, 3), weight=1)
            self.configure(fg_color="transparent")
            
            # define Discard changes button
            self._btn_discard = customtkinter.CTkButton(self, text="Discard changes", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_discard)
            self._btn_discard.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

            # define Start button
            self._btn_start = customtkinter.CTkButton(self, text="Start", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_start)
            self._btn_start.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")

            # define Save button
            self._btn_save = customtkinter.CTkButton(self, text="Save", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_save)
            self._btn_save.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")

            # define Save and Start button
            self._btn_save_start = customtkinter.CTkButton(self, text="Save and Start", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_save_start)
            self._btn_save_start.grid(row=0, column=3, padx=5, pady=5, sticky="nswe")

        except Exception:
            self.master.error_handle("ERROR", "Unable to create GUI - buttons", terminate=True)


    def _btn_callback_discard(self) -> None:
        """Callback function for the discard button. Opens a new toplevel window."""
        tpe = "WARNING!"
        msge = "All changes you made will not be saved."
        ques = "Do you really want to proceed?"
        self.master.open_toplevel_yn(tpe, msge, ques, self.master.exit_program, self.master.kill_toplevel)
        return
    

    def _btn_callback_start(self) -> None:
        """Callback function for the start button."""
        self.master.conn.send("RUN-PROP")
        return
    

    def _btn_callback_save(self) -> None:
        self.master.save()
        return
    

    def _btn_callback_save_start(self) -> None:
        """Callback function for the Save and Start button. Defined via AppInterface."""
        self.master.save()
        self.master.conn.send("RUN-PROP")
        return


    def disable_buttons(self) -> None:
        """Makes several buttons unclickable"""
        try:
            self._btn_discard.configure(state="disabled")
            self._btn_start.configure(state="disabled")
            self._btn_save_start.configure(state="disabled")

        except Exception:
            self.master.error_handle("WARNING", "Unable to disable buttos", terminate=False)

        return
    

    def enable_buttons(self) -> None:
        """Restores buttons to be clickable again"""
        try:
            self._btn_discard.configure(state="normal")
            self._btn_start.configure(state="normal")
            self._btn_save_start.configure(state="normal")

        except Exception:
            self.master.error_handle("WARNING", "Unable to enable buttos", terminate=False)

        return


# ================================================================================================================================

class App(customtkinter.CTk):
    """Main GUI window class. Container for all of the frames.
    
    Child of customtkinter.CTk.
    
    Attributes
    ----------
    - my_config : json
    - toplevel_window
    - database_frame : DatabaseFrame
    - process_frame : ProcessFrame
    - text_box : TextboxFrame
    - progress_bar : ProgressFrame
    - button_frame : ButtonsFrame
        
    Methods
    -------
    - open_config()
    - open_toplevel_yn(type, mesage, question, callback_yes, callback_no)
    - open_toplevel_ok(type, message)
    - kill_toplevel()
    - save()
    """

    def __init__(self):
        super().__init__()

        self.conn = None

        try:
            # set colors
            customtkinter.set_appearance_mode("system")
            self.col_frame_title_bg = "#5e5e5e"
            self.col_frame_title_tx = "white"
            self.col_popup_yn_bg = "orange"
            self.col_popup_yn_lab = "white"
            self.col_popup_yn_tx = "black"
            self.col_popup_ok_bg = "orange"
            self.col_popup_ok_lab = "white"
            self.col_popup_ok_tx = "black"
            self.col_progress_bg = "#dbdbdb"
            self.col_progress_bar = "#21cc29"
            self.col_btn_tx = "white"
            self.col_btn_dis_tx = "#1d4566"

            self.my_config = self.open_config()
            self.toplevel_window = None

            self.title("MF4 Signal converter")
            self.minsize(650, 700)
            self.protocol("WM_DELETE_WINDOW", self._closing_handle)

            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)

            self.database_frame = DatabaseFrame(self)
            self.database_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
            
            self.process_frame = ProcessFrame(self)
            self.process_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

            self.text_box = TextboxFrame(self)
            self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nswe")

            self.progress_bar = ProgressFrame(self)
            self.progress_bar.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="nswe")

            self.button_frame = ButtonsFrame(self)
            self.button_frame.grid(row=3, column=0, padx=5, pady=10, columnspan=2, sticky="nswe")


        except Exception as e:
            print()
            print(f"ERROR while trying to initialize GUI window: {e}")


    def exit_program(self) -> None:
        self.kill_toplevel()
        self.open_toplevel_exit()
        self.conn.send("END")
        return


    def kill_main_window(self) -> None:
        # delay so that popup can load properly
        time.sleep(1)
        self.kill_toplevel()
        self.quit()
        return

    
    def open_config(self):
        """Loads configure json file (config.json) from root directory. Returns json object."""
        try:
            with open(os.path.join("src", "config.json"), "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            print()
            print("ERROR while reading src\\config.json file. Check for file existance.")
            self.exit_program()
    
        return data
    
    
    def open_toplevel_yn(self, type: str, message: str, question: str, callback_yes, callback_no) -> None:
        """Opens a toplevel window over the main window with given parameters and YES/NO buttons.
        
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
        None"""

        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # create toplevel window
            self.toplevel_window = TopWindowYesNo(self, type, message, question, callback_yes, callback_no)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def open_toplevel_ok(self, type: str, message: str, callback: callable = None) -> None:
        """Opens a toplevel window over the main window with given message and OK button.
        
        Parametres
        ----------
        - type : str
            - Name of the window
        - message : str
            - Displayed message in the white box
            
        Returns
        -------
        None"""

        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # create toplevel window
            self.toplevel_window = TopWindowOk(self, type, message, callback)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def open_toplevel_exit(self) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # create toplevel window
            self.toplevel_window = TopWindowExit(self)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def save(self) -> None:
        """Saves all possible changes into the config.json file."""
        if self.database_frame.save_to_json() and self.process_frame.save_to_json():
            self.text_box.write(f"Successfully saved!\n")
            # update backend configuration
            self.conn.send("U-CONF")
        else:
            self.text_box.write(f"Failed to save.\n")

        # redraw 
        self.database_frame.refresh()
        self.process_frame.refresh()

        return
    

    def set_connection(self, connection) -> None:
        """Sets the connection stream"""
        self.conn = connection
        return
    

    def kill_toplevel(self) -> None:
        """Destroys the toplevel window"""
        if self.toplevel_window is not None:
            self.toplevel_window.destroy()
            self.toplevel_window.update()
        return
    

    def _closing_handle(self) -> None:
        self.open_toplevel_yn("WARNING", "Do you really want to exit?", "", self.exit_program, self.kill_toplevel)
        return
    

    def error_handle(self, type: str, message: str, terminate: bool) -> None:
        """Creates an error popup on demand with the possibility of program termination"""
        if terminate:
            callback = self.exit_program
        else:
            callback = self.kill_toplevel
        
        self.open_toplevel_ok(type, message, callback)
        return
