import customtkinter
import json
import sys


class TopWindowYesNo(customtkinter.CTkToplevel):
    def __init__(self, type: str, msg: str, btn_callback_yes=None, btn_callback_no=None):
        super().__init__()

        self.minsize(300, 150)
        self.resizable(False, False)
        self.title(type)
        self.configure(fg_color="orange")

        self.grid_columnconfigure((0, 1), weight=1)
        
        # bring the window into the foregroud
        self.after(50, self.lift)

        # Message
        self.label = customtkinter.CTkLabel(self, text=msg, fg_color="white")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 0), sticky="nswe")

        # Do you really want to proceed?
        self.label = customtkinter.CTkLabel(self, text="Do you really want to proceed?")
        self.label.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nswe")

        # YES button
        self.btn_start = customtkinter.CTkButton(self, text="Yes", command=btn_callback_yes)
        self.btn_start.grid(row=2, column=0, padx=10, pady=10, sticky="nswe")

        # NO button
        self.btn_start = customtkinter.CTkButton(self, text="No", command=btn_callback_no)
        self.btn_start.grid(row=2, column=1, padx=10, pady=10, sticky="nswe")
        
        

class DatabaseFrame(customtkinter.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        self.my_config = config

        # Frame title
        self.title = customtkinter.CTkLabel(self, text="Database configuration", fg_color="orange", corner_radius=6)
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        
        # define entry names
        entry_names = [("Host", "host"),
                       ("Port", "port"),
                       ("Database", "database"),
                       ("User", "user"),
                       ("Password", "password"),
                       ("Schema", "schema_name")]
        self.entries = []
        self.labels = []
        # create entries
        for i, name in enumerate(entry_names):
            label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
            label.grid(row=i+1, column=0, padx=15, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, placeholder_text=self.my_config["database"][name[1]])
            entry.grid(row=i+1, column=1, padx=10, pady=10, sticky="we")

            self.labels.append(label)
            self.entries.append(entry)


    def get(self) -> list:
        result = []
        for entry in self.entries:
            result.append(entry.get())
        return result
    
    def save_to_json(self) -> None:
        return
    


class ProcessFrame(customtkinter.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.my_config = config

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

            if self.my_config["settings"][name[1]]:
                switch.select()

            self.switches.append(switch)

        # define entry names
        entry_names = [("Agg. max skip seconds", "agg_max_skip_seconds")]
        self.entries = []
        self.labels = []
        # create entries
        for i, name in enumerate(entry_names):
            label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
            label.grid(row=i+1+len(self.switches), column=0, padx=10, pady=10, sticky="w")
            entry = customtkinter.CTkEntry(self, placeholder_text=self.my_config["settings"][name[1]])
            entry.grid(row=i+1+len(self.switches), column=1, padx=10, pady=10, sticky="we")

            self.labels.append(label)
            self.entries.append(entry)


    def get(self) -> list:
        result = []
        for switch in self.switches:
            result.append(switch.get())
        for entry in self.entries:
            result.append(entry.get())
        return result
    
    def save_to_json(self) -> None:
        return



class TextboxFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # frame title
        self.title = customtkinter.CTkLabel(self, text="Feedback prompt", fg_color="transparent")
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        
        # define textbox
        self.textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, activate_scrollbars=True, wrap="word")
        self.textbox.grid(row=1, column=0, sticky="nsew")


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
    def __init__(self, master, db_frame, proc_frame, txt_box, top_window, progress):
        super().__init__(master)

        self.database_frame = db_frame
        self.process_frame = proc_frame
        self.text_box = txt_box
        self.toplevel_warning = top_window
        self.progress_bar = progress

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.configure(fg_color="transparent")
        
        # define Discard changes button
        self.btn_discard = customtkinter.CTkButton(self, text="Discard changes", command=self.btn_callback_discard)
        self.btn_discard.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

        # define Start button
        self.btn_start = customtkinter.CTkButton(self, text="Start", command=self.btn_callback_start)
        self.btn_start.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")

        # define Save button
        self.btn_save = customtkinter.CTkButton(self, text="Save", command=self.btn_callback_save)
        self.btn_save.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")

        # define Save and Start button
        self.btn_save_start = customtkinter.CTkButton(self, text="Save and Start", command=self.btn_callback_savestart)
        self.btn_save_start.grid(row=0, column=3, padx=5, pady=5, sticky="nswe")


    def btn_callback_discard(self) -> None:
        self.open_toplevel("WARNING!", "Any changes you made will not be saved.", yes_fc=self.exit_program, no_fc=self.kill_toplevel_window)
        return
    
    def btn_callback_start(self) -> None:
        self.start_process()
        return
    
    def btn_callback_save(self) -> None:
        self.save()
        return
    
    def btn_callback_savestart(self) -> None:
        self.save()
        self.start_process()
        return
    
    def start_process(self) -> None:
        self.disable_buttons()
        # check if clean upload is selected

        # start process
        self.progress_bar.show()

        return 

    def save(self) -> None:
        self.text_box.write(f"Database: {self.database_frame.get()}\n")
        self.text_box.write(f"Settings: {self.process_frame.get()}\n")

        # save json file
        self.database_frame.save_to_json()
        self.process_frame.save_to_json()

        # load new settings


        # redraw 

        return
    
    def disable_buttons(self) -> None:
        self.btn_discard.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_save_start.configure(state="disabled")
    
    def restore_buttons(self) -> None:
        self.btn_discard.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_save_start.configure(state="normal")

    def open_toplevel(self,type: str, msg: str, yes_fc=None, no_fc=None) -> None:
        if self.toplevel_warning is None or not self.toplevel_warning.winfo_exists():
            self.toplevel_warning = TopWindowYesNo(type, msg, yes_fc, no_fc)

    def exit_program(self) -> None:
        sys.exit(0)
    
    def kill_toplevel_window(self) -> None:
        # delete the window
        self.toplevel_warning.destroy()
        self.toplevel_warning.update()





class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.my_config = self.open_config()
        self.toplevel_window = None

        self.title("Simple test")
        self.minsize(650, 700)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.database_frame = DatabaseFrame(self, self.my_config)
        self.database_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        
        self.process_frame = ProcessFrame(self, self.my_config)
        self.process_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

        self.text_box = TextboxFrame(self)
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nswe")

        self.progress_bar = ProgressFrame(self)
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="nswe")

        self.button_frame = ButtonsFrame(self, self.database_frame, self.process_frame, self.text_box, self.toplevel_window, self.progress_bar)
        self.button_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky="nswe")


    def btn_callback(self):
        self.text_box.write(f"You selected: {self.process_frame.get()}\n")
        print("Database: ", self.database_frame.get())
        print("Process: ", self.process_frame.get())

    def open_config(self):
        """Loads configure json file (config.json) from root directory. Returns json object."""
        try:
            file = open("config.json", "r")
            data = json.load(file)
            file.close()

        except FileNotFoundError:
            print()
            print("ERROR while reading config.json file. Check for file existance.")
            sys.exit(1)
    
        return data


app = App()
app.mainloop()