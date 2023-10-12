import customtkinter
import json
import sys


class AppInterface():
    def __init__(self, app):
        self.app = app

    
    def generate_pop_up(self, type: str, message: str, question: str, callback_yes, callback_no) -> None:
        """Generates a desired popup window with YES and NO buttons
        
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

        self.app.open_toplevel(type, message, question, callback_yes, callback_no)
        return
    

    def kill_pop_up(self) -> None:
        """Closes the currently open toplevel pop-up"""
        app.kill_toplevel()
        return
    

    def print_to_box(self, message: str) -> None:
        """Prints the given message into the GUI textbox
        
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
        """Sets desired callback start function to the Start and SaveStart button
        
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
        """Saves changes made in the GUI to src\config.json file
        
        Returns
        -------
        None"""

        self.app.save()
        return
    

    def disable_buttons(self) -> None:
        """Disables following buttons: btn_save_start, btn_discard, btn_start
        
        Returns
        -------
        None"""

        self.app.button_frame.disable_buttons()
        return
    

    def enable_buttons(self) -> None:
        """Enables following buttons: btn_save_start, btn_discard, btn_start
        
        Returns
        -------
        None"""

        self.app.button_frame.enable_buttons()
        return
    
    
    def show_progress_bar(self) -> None:
        """Shows the progress bar under the textbox
        
        Returns
        -------
        None"""

        self.app.progress_bar.show()
        return
    

    def hide_progress_bar(self) -> None:
        """Hides the progress bar under the textbox
        
        Returns
        -------
        None"""  

        self.app.progress_bar.hide()
        return
    

    def update_progress_bar(self, value) -> None:
        """Updates the progress bar to the given value
        
        Parametres
        ----------
        - value
            - float value of progress, between 0 and 1
            
        Returns
        -------
        None"""

        self.app.progress_bar.set_value(value)
        return



class TopWindowYesNo(customtkinter.CTkToplevel):
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
        
        

class DatabaseFrame(customtkinter.CTkFrame):
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


    def get(self) -> list:
        result = []
        for entry in self.entries:
            result.append(entry[0].get())
        return result
    

    def refresh(self) -> None:
        for entry in self.entries:
            entry[0].configure(placeholder_text=self.master.my_config["database"][entry[1]])
    
    
    def save_to_json(self) -> None:
        # update config
        for entry in self.entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                self.master.my_config["database"][entry[1]] = val

        # write to the file:
        with open("config.json", "w") as file:
            json.dump(self.master.my_config, file, indent=4)

    

class ProcessFrame(customtkinter.CTkFrame):
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


    def get(self) -> list:
        result = []
        for switch in self.switches:
            result.append(switch[0].get())
        for entry in self.entries:
            result.append(entry[0].get())
        return result
    
    
    def refresh(self) -> None:
        for entry in self.entries:
            entry[0].configure(placeholder_text=self.master.my_config["settings"][entry[1]])
    

    def save_to_json(self) -> None:
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
                    val = str(entry[0].get())
                # save
                self.master.my_config["settings"][entry[1]] = val

        # write to the file:
        with open("config.json", "w") as file:
            json.dump(self.master.my_config, file, indent=4)



class TextboxFrame(customtkinter.CTkFrame):
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
        self.textbox.configure(state="disabled")


    def write(self, msg: str) -> None:
        self.textbox.configure(state="normal")
        self.textbox.insert("end", msg)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")



class ProgressFrame(customtkinter.CTkFrame):
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
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        self.progress.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")

    def hide(self) -> None:
        self.title.grid_forget()
        self.progress.grid_forget()

    def set_value(self, val) -> None:
        self.progress.set(val)



class ButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.toplevel_warning = self.master.toplevel_window

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.start_function = None
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
        tpe = "WARNING!"
        msge = "All changes you made will not be saved."
        ques = "Do you really want to proceed?"
        self.master.open_toplevel(tpe, msge, ques, self.exit_program, self.master.kill_toplevel)
        return
    

    def btn_callback_start(self) -> None:
        # runtime-defined
        if self.start_function is not None:
            self.start_function()

        return
    

    def btn_callback_save_start(self) -> None:
        self.master.save()
        # runtime-defined
        if self.start_function is not None:
            self.start_function()
        return


    def disable_buttons(self) -> None:
        self.btn_discard.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_save_start.configure(state="disabled")
    

    def enable_buttons(self) -> None:
        self.btn_discard.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_save_start.configure(state="normal")


    def exit_program(self) -> None:
        sys.exit(0)



class App(customtkinter.CTk):
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
            with open("config.json", "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            print()
            print("ERROR while reading config.json file. Check for file existance.")
            sys.exit(1)
    
        return data
    
    
    def open_toplevel(self, type: str, message: str, question: str, callback_yes, callback_no) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # create toplevel window
            self.toplevel_window = TopWindowYesNo(type, message, question, callback_yes, callback_no)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return
    

    def save(self) -> None:
        self.database_frame.save_to_json()
        self.process_frame.save_to_json()

        # redraw 
        self.database_frame.refresh()
        self.process_frame.refresh()

        self.text_box.write(f"Successfully saved!\n")
        return
    

    def kill_toplevel(self) -> None:
        self.toplevel_window.destroy()
        self.toplevel_window.update()
        return


app = App()
app.mainloop()