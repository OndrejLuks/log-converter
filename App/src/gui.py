# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com

# ================================================================================================================================
# ================================================================================================================================

import customtkinter
import json
import sys
import os

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
    - set_start_function (function)
    - save_changes ()
    - disable_buttons ()
    - enable_buttons ()
    - show_progress_bar ()
    - hide_progress_bar ()
    - update_progress_bar ()
    """

    def __init__(self, app):
        """Constructior of AppInterface"""
        self.app = app

    
    def run(self) -> None:
        """Runs and shows the GUI application
        
        Returns
        -------
        None
        """

        self.app.mainloop()
        return
    
    
    def generate_pop_up_yn(self, type: str, message: str, question: str, callback_yes, callback_no) -> None:
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
        None"""

        self.app.open_toplevel_yn(type, message, question, callback_yes, callback_no)
        return
    

    def generate_pop_up_ok(self, type: str, message: str) -> None:
        """Generates a message popup window with OK button.
        
        Parametres
        ----------
        - type : str
            - Name of the window
        - message : str
            - Displayed message in the white box
            
        Returns
        -------
        None"""

        self.app.open_toplevel_ok(type, message)
        return
    

    def kill_pop_up(self) -> None:
        """Closes the currently open toplevel pop-up"""
        self.app.kill_toplevel()
        return
    

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
    

    def set_start_function(self, function) -> None:
        """Sets desired callback start function to the Start and SaveStart button.
        
        Parametres
        ----------
        - function
            - This function will be assigned as a callback to the buttons
            
        Returns
        -------
        None"""

        if not callable(function):
            raise ValueError("The provided parameter is not a function!")

        self.app.button_frame.start_function = function
        return
    

    def save_changes(self) -> None:
        """Saves changes made in the GUI to src\config.json file.
        
        Returns
        -------
        None"""

        self.app.save()
        return
    

    def disable_buttons(self) -> None:
        """Disables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.disable_buttons()
        return
    

    def enable_buttons(self) -> None:
        """Enables following buttons: btn_save_start, btn_discard, btn_start.
        
        Returns
        -------
        None"""

        self.app.button_frame.enable_buttons()
        return
    
    
    def show_progress_bar(self) -> None:
        """Shows the progress bar under the textbox.
        
        Returns
        -------
        None"""

        self.app.progress_bar.show()
        return
    

    def hide_progress_bar(self) -> None:
        """Hides the progress bar under the textbox.
        
        Returns
        -------
        None"""  

        self.app.progress_bar.hide()
        return
    

    def update_progress_bar(self, value) -> None:
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

    def __init__(self, type: str, msg: str, question: str, btn_callback_yes=None, btn_callback_no=None):
        super().__init__()

        self.minsize(300, 150)
        self.resizable(False, False)
        self.title(type)
        self.configure(fg_color="orange")

        self.grid_columnconfigure((0, 1), weight=1)
        
        # bring the window into the foregroud
        self.after(50, self.lift)

        # Message
        self.msg = customtkinter.CTkLabel(self, text=msg, fg_color="white", corner_radius=6)
        self.msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 0), sticky="nswe")

        # Do you really want to proceed?
        self.question = customtkinter.CTkLabel(self, text=question)
        self.question.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nswe")

        # YES button
        self.btn_yes = customtkinter.CTkButton(self, text="Yes", command=btn_callback_yes)
        self.btn_yes.grid(row=2, column=0, padx=10, pady=10, sticky="nswe")

        # NO button
        self.btn_no = customtkinter.CTkButton(self, text="No", command=btn_callback_no)
        self.btn_no.grid(row=2, column=1, padx=10, pady=10, sticky="nswe")
        
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

    def __init__(self, type: str, msg: str):
        super().__init__()

        self.minsize(300, 120)
        self.resizable(False, False)
        self.title(type)
        self.configure(fg_color="orange")
        self.grid_columnconfigure(0, weight=1)
       
        # bring the window into the foregroud
        self.after(50, self.lift)

        # Message
        self.msg = customtkinter.CTkLabel(self, text=msg, fg_color="white", corner_radius=6)
        self.msg.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="nswe")

        # OK button
        self.btn_ok = customtkinter.CTkButton(self, text="Okay", command=self.close)
        self.btn_ok.grid(row=1, column=0, padx=10, pady=10, sticky="swe")


    def close(self) -> None:
        """Destroys the toplevel window"""
        self.destroy()
        self.update()
        return
        
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Frame title
        self.title = customtkinter.CTkLabel(self, text="Database configuration", fg_color="orange", corner_radius=6)
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        
        # define entry names
        self.entry_names = [("Host", "host"),
                       ("Port", "port"),
                       ("Database", "database"),
                       ("User", "user"),
                       ("Password", "password"),
                       ("Schema", "schema_name")]
        self.entries = []
        self.labels = []

        # create entries
        for i, name in enumerate(self.entry_names):
            label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
            label.grid(row=i+1, column=0, padx=15, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, placeholder_text=self.master.my_config["database"][name[1]])
            entry.grid(row=i+1, column=1, padx=10, pady=10, sticky="we")

            self.labels.append(label)
            self.entries.append((entry, name[1]))


    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self.entries:
            entry[0].configure(placeholder_text=self.master.my_config["database"][entry[1]])

        return
    
    
    def save_to_json(self) -> bool:
        """Saves database settings changes into the config.json file"""
        # update config
        for entry in self.entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                self.master.my_config["database"][entry[1]] = val

        # write to the file:
        with open(os.path.join("src", "config.json"), "w") as file:
            json.dump(self.master.my_config, file, indent=4)

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

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Frame title
        self.title = customtkinter.CTkLabel(self, text="Process configuration", fg_color="orange", corner_radius=6)
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        # define switch names
        switch_names = [("Aggregate", "aggregate"),
                        ("Move done files", "move_done_files"),
                        ("Write time info", "write_time_info"),
                        ("Clean upload", "clean_upload")]
        self.switches = []

        # create switches
        for i, name in enumerate(switch_names):
            switch = customtkinter.CTkSwitch(self, text=name[0])
            switch.grid(row=i+1, column=0, columnspan=2, padx=10, pady=10, sticky="w")

            # set default switch position
            if self.master.my_config["settings"][name[1]]:
                switch.select()

            self.switches.append((switch, name[1]))

        # define entry names
        entry_names = [("Agg. max skip seconds", "agg_max_skip_seconds")]
        self.entries = []
        self.labels = []
        # create entries
        for i, name in enumerate(entry_names):
            label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
            label.grid(row=i+1+len(self.switches), column=0, padx=10, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, placeholder_text=self.master.my_config["settings"][name[1]])
            entry.grid(row=i+1+len(self.switches), column=1, padx=10, pady=10, sticky="we")

            self.labels.append(label)
            self.entries.append((entry, name[1]))
    
    
    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self.entries:
            entry[0].configure(placeholder_text=self.master.my_config["settings"][entry[1]])

        return
    

    def save_to_json(self) -> bool:
        """Saves process settings changes into the config.json file"""
        # update config
        for switch in self.switches:
            val = int(switch[0].get())
            if val == 1:
                self.master.my_config["settings"][switch[1]] = True
            if val == 0:
                self.master.my_config["settings"][switch[1]] = False

        for entry in self.entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                # try to convert numbers from entries into string
                try:
                    val = int(val)

                except ValueError:
                    self.master.open_toplevel_ok("WARNING", f'"{val}" is not a number!')
                    return False
                
                # save
                self.master.my_config["settings"][entry[1]] = val

        # write to the file:
        with open(os.path.join("src", "config.json"), "w") as file:
            json.dump(self.master.my_config, file, indent=4)
        
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # frame title
        self.title = customtkinter.CTkLabel(self, text="Feedback prompt", fg_color="transparent")
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        
        # define textbox
        self.textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, activate_scrollbars=True, wrap="word")
        self.textbox.grid(row=1, column=0, sticky="nsew")
        self.textbox.configure(state="disabled", font=("Courier New", 12))


    def write(self, msg: str = "\n") -> None:
        """Prints the given message to the GUI's textbox.
        
        Parameters
        ----------
        - msg : str
            - message to be printed
        """
        # make the textbox writeable
        self.textbox.configure(state="normal")
        # insert message at the end
        self.textbox.insert("end", msg)
        # scroll to the end
        self.textbox.see("end")
        # make the textbox non-writeable
        self.textbox.configure(state="disabled")
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

        self.configure(fg_color="transparent", height=15)
        self.grid_columnconfigure(1, weight=1)

        # frame title
        self.title = customtkinter.CTkLabel(self, text="Progress", fg_color="transparent", height=1)
        self.title.grid_forget()
        
        # define progress bar
        self.progress = customtkinter.CTkProgressBar(master=self, mode="determinate", corner_radius=0, progress_color=("green", "green"), height=1)
        self.progress.set(0)
        self.progress.grid_forget()

    def show(self) -> None:
        """Shows this object inside the master window."""
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        self.progress.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")
        return

    def hide(self) -> None:
        """Hides this object within the master window."""
        self.title.grid_forget()
        self.progress.grid_forget()
        return

    def set_value(self, val: float) -> None:
        """Sets given value to the progress bar.

        Parameters
        ----------
        - val : float
            - only numbers from closed interval <0 to 1>
        """
        self.progress.set(val)
        return

# ================================================================================================================================

class ButtonsFrame(customtkinter.CTkFrame):
    """Class representing the frame for buttons.
    
    Child of customtkinter.CTkFrame.
    
    Attributes
    ----------
    - start_function : callable
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
        self.start_function = None

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.configure(fg_color="transparent")
        
        # define Discard changes button
        self.btn_discard = customtkinter.CTkButton(self, text="Discard changes", text_color_disabled="orange", command=self.btn_callback_discard)
        self.btn_discard.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

        # define Start button
        self.btn_start = customtkinter.CTkButton(self, text="Start", text_color_disabled="orange", command=self.btn_callback_start)
        self.btn_start.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")

        # define Save button
        self.btn_save = customtkinter.CTkButton(self, text="Save", text_color_disabled="orange", command=self.master.save)
        self.btn_save.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")

        # define Save and Start button
        self.btn_save_start = customtkinter.CTkButton(self, text="Save and Start", text_color_disabled="orange", command=self.btn_callback_save_start)
        self.btn_save_start.grid(row=0, column=3, padx=5, pady=5, sticky="nswe")


    def btn_callback_discard(self) -> None:
        """Callback function for the discard button. Opens a new toplevel window."""
        tpe = "WARNING!"
        msge = "All changes you made will not be saved."
        ques = "Do you really want to proceed?"
        self.master.open_toplevel_yn(tpe, msge, ques, self.exit_program, self.master.kill_toplevel)
        return
    

    def btn_callback_start(self) -> None:
        """Callback function for the start button. Defined via AppInterface."""
        # runtime-defined
        if self.start_function is not None:
            self.start_function()

        return
    

    def btn_callback_save_start(self) -> None:
        """Callback function for the Save and Start button. Defined via AppInterface."""
        self.master.save()
        # runtime-defined
        if self.start_function is not None:
            self.start_function()
        return


    def disable_buttons(self) -> None:
        """Makes several buttons unclickable"""
        self.btn_discard.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_save_start.configure(state="disabled")
        return
    

    def enable_buttons(self) -> None:
        """Restores buttons to be clickable again"""
        self.btn_discard.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_save_start.configure(state="normal")
        return


    def exit_program(self) -> None:
        sys.exit(0)

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

        self.my_config = self.open_config()
        self.toplevel_window = None

        self.title("MF4 Signal converter")
        self.minsize(650, 700)

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
        self.button_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky="nswe")


    def open_config(self):
        """Loads configure json file (config.json) from root directory. Returns json object."""
        try:
            with open(os.path.join("src", "config.json"), "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            print()
            print("ERROR while reading src\config.json file. Check for file existance.")
            sys.exit(1)
    
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
            self.toplevel_window = TopWindowYesNo(type, message, question, callback_yes, callback_no)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def open_toplevel_ok(self, type: str, message: str) -> None:
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
            self.toplevel_window = TopWindowOk(type, message)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def save(self) -> None:
        """Saves all possible changes into the config.json file."""
        if self.database_frame.save_to_json() and self.process_frame.save_to_json():
            self.text_box.write(f"Successfully saved!\n")
        else:
            self.text_box.write(f"Failed to save.\n")

        # redraw 
        self.database_frame.refresh()
        self.process_frame.refresh()

        return
    

    def kill_toplevel(self) -> None:
        """Destroys the toplevel window"""
        self.toplevel_window.destroy()
        self.toplevel_window.update()
        return
