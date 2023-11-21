# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from tkcalendar import Calendar
from tkinter import filedialog
import customtkinter
import json
import time
import os

# ================================================================================================================================
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


class FolderSelectorFrame(customtkinter.CTkFrame):
    def __init__(self, master, str_label, str_btn, str_current):
        super().__init__(master)

        self._str_label = str_label

        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=5)

        self._select_label = customtkinter.CTkLabel(self, text=(str_label + ":"), fg_color="transparent")
        self._select_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self._btn = customtkinter.CTkButton(self, text=str_btn, text_color=self.master.master.col_btn_tx, text_color_disabled=self.master.master.col_btn_dis_tx, command=self._btn_callback)
        self._btn.grid(row=0, column=2, padx=10, pady=10, sticky="we")

        self._current_label = customtkinter.CTkLabel(self, text=(str_current + ":"), fg_color="transparent")
        self._current_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self._current = customtkinter.CTkEntry(self, placeholder_text="Current directory here")
        self._current.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="we")

    
    def _btn_callback(self) -> None:
        dir_path = filedialog.askdirectory(title=self._str_label, initialdir=".")

        if dir_path:
            self.change_curr_dir(dir_path)
        
        return
    
    def change_curr_dir(self, new_dir) -> None:
        # clear the entry
        self._current.delete(0, 'end')
        # set new entry
        self._current.insert(0, new_dir)
        return

    def get_curr_dir(self) -> str:
        return str(self._current.get())


# ================================================================================================================================


class BeforeStartFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=5)

        # Frame title
        self._title = customtkinter.CTkLabel(self, text="Before start", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
        self._title.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="we")

        # MF4 files
        self._mf4_select = FolderSelectorFrame(self, "Select MF4 files root directory", "Select MF4 dir", "Current MF4 dir")
        self._mf4_select.change_curr_dir(self.get_curr_dir_path("mf4_path"))
        self._mf4_select.grid(row=1, column=0, columnspan=3, padx=0, pady=(0, 40), sticky="we")

        # DBC files
        self._dbc_select = FolderSelectorFrame(self, "Select DBC files root directory", "Select DBC dir", "Current DBC dir")
        self._dbc_select.change_curr_dir(self.get_curr_dir_path("dbc_path"))
        self._dbc_select.grid(row=2, column=0, columnspan=3, padx=0, pady=0, sticky="we")

    
    def get_curr_dir_path(self, path_of: str) -> str:
        return self.master.get_curr_dir_path(path_of)
    

    def save_curr_paths(self) -> bool:
        mf4_path = self._mf4_select.get_curr_dir()
        dbc_path = self._dbc_select.get_curr_dir()

        if len(mf4_path) == 0:
            self.master.error_handle("WARNING", "Path to MF4 files is blank!", False)
            return False
        
        if len(dbc_path) == 0:
            self.master.error_handle("WARNING", "Path to DBC files is blank!", False)
            return False
        
        if not self.master.update_local_config("settings", "mf4_path", mf4_path):
            return False
        
        if not self.master.update_local_config("settings", "dbc_path", dbc_path):
            return False
        
        return self.master.write_config_to_file() and self.master.write_config_to_file() 
    

# ================================================================================================================================


class TimeSelectorFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        try:
            self.configure(fg_color="transparent")

            self.grid_columnconfigure((0, 2, 4), weight=10)
            self.grid_columnconfigure((1, 3), weight=1)

            self._entry_width = 30
            self._entries = []

            # hh
            hh = customtkinter.CTkEntry(self, placeholder_text="hh", width=self._entry_width)
            hh.grid(row=0, column=0, padx=0, pady=0, sticky="nswe")
            self._entries.append((hh, "hours"))
            # :
            self._col1 = customtkinter.CTkLabel(self, text=":", fg_color="transparent")
            self._col1.grid(row=0, column=1, padx=5, pady=0, sticky="nswe")
            # mm
            mm = customtkinter.CTkEntry(self, placeholder_text="mm", width=self._entry_width)
            mm.grid(row=0, column=2, padx=0, pady=0, sticky="nswe")
            self._entries.append((mm, "minutes"))
            # :
            self._col2 = customtkinter.CTkLabel(self, text=":", fg_color="transparent")
            self._col2.grid(row=0, column=3, padx=5, pady=0, sticky="nswe")
            # ss
            ss = customtkinter.CTkEntry(self, placeholder_text="ss", width=self._entry_width)
            ss.grid(row=0, column=4, padx=0, pady=0, sticky="nswe")
            self._entries.append((ss, "seconds"))

        except Exception as e:
            self.master.master.master.error_handle("ERROR", f"Unable to create GUI - time entry:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------
    
    def get_values(self) -> list:
        output = []

        for entry in self._entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                output.append(val)
            else:
                self.master.master.master.text_box.write(f"WARNING: Time {entry[1]} missing, 00 set as default!\n")
                output.append("00")

        return output


# ================================================================================================================================


class DateTimePickerFrame(customtkinter.CTkFrame):
    def __init__(self, master, title: str):
        super().__init__(master)

        try:
            self.grid_columnconfigure(0, weight=1)
            self.configure(fg_color="transparent")

            # title
            self._time_select_label = customtkinter.CTkLabel(self, text=title, fg_color="transparent")
            self._time_select_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

            # callendar
            self._calendar = Calendar(self, selectmode="day", showweeknumbers=False, cursor="hand2", date_pattern="y-mm-dd", borderwidth=0, bordercolor="white")
            self._calendar.grid(row=2, column=0, padx=10, pady=5, sticky="we")

            # time
            self._time_entry = TimeSelectorFrame(self)
            self._time_entry.grid(row=3, column=0, padx=10, pady=5, sticky="we")
        
        except Exception as e:
            self.master.master.error_handle("ERROR", f"Unable to create GUI - date entry:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def get_values(self) -> dict:
        time_val = self._time_entry.get_values()
        date_val = self._calendar.get_date().split("-")
        return {"date" : {"y" : date_val[0], "m" : date_val[1], "d" : date_val[2]},
                "time" : {"h" : time_val[0], "m" : time_val[1], "s" : time_val[2]}}


# ================================================================================================================================


class DownloadFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(6, weight=1)
            self.configure(fg_color="transparent")

            self._signal = ""
            self._signals = ["none"]

            # frame title
            self._title = customtkinter.CTkLabel(self, text="Data download", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")

            # load signals
            self._load_frame = customtkinter.CTkFrame(self)
            self._load_frame.grid_columnconfigure(0, weight=1)
            self._load_frame.grid_columnconfigure(1, weight=4)
            self._load_frame.configure(fg_color="transparent", corner_radius=0)

            self._sig_load_label = customtkinter.CTkLabel(self._load_frame, text="Load signals:", fg_color="transparent")
            self._sig_load_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            self._btn_load = customtkinter.CTkButton(self._load_frame, text="Load from DB", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_load)
            self._btn_load.grid(row=0, column=1, padx=10, pady=5, sticky="nswe")

            self._load_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="we")

            # signal selection
            self._select_frame = customtkinter.CTkFrame(self)
            self._select_frame.grid_columnconfigure(0, weight=1)
            self._select_frame.grid_columnconfigure(1, weight=4)
            self._select_frame.configure(fg_color="transparent", corner_radius=0)

            self._sig_select_label = customtkinter.CTkLabel(self._select_frame, text="Select signal:", fg_color="transparent")
            self._sig_select_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            self._option_menu = customtkinter.CTkOptionMenu(self._select_frame, values=self._signals, command=self._combo_callback)
            self._option_menu.grid(row=0, column=1, padx=10, pady=5, sticky="nswe")

            self._select_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky="we")

            # from date-time
            self._date_time_from = DateTimePickerFrame(self, "Select FROM time stamp:")
            self._date_time_from.grid(row=5, column=0, padx=(0, 10), pady=(10, 5), sticky="nswe")

            # to date-time
            self._date_time_to = DateTimePickerFrame(self, "Select TO time stamp:")
            self._date_time_to.grid(row=5, column=1, padx=(10, 0), pady=(10, 5), sticky="nswe")

            # download button
            self._btn_download = customtkinter.CTkButton(self, text="Download as csv", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_download)
            self._btn_download.grid(row=6, column=0, columnspan=2, padx=200, pady=(10, 0), sticky="swe")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - download:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def _combo_callback(self, choice) -> None:
        self._signal = str(choice)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_load(self) -> None:
        self._signals.clear()
        # fetch signals from the database
        self.master.comm.send_command("FETCH-SIG")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_download(self) -> None:
        if self._signal == "":
            self.master.error_handle("WARNING", "Signal not selected!", False)
            return

        try:
            file_path = filedialog.asksaveasfile(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                from_t = self._date_time_from.get_values()
                to_t = self._date_time_to.get_values()

                # format "yyyy-mm-dd hh-ss-mm"
                from_str = f"{from_t['date']['y']}-{from_t['date']['m']}-{from_t['date']['d']} {from_t['time']['h']}:{from_t['time']['m']}:{from_t['time']['s']}"
                to_str = f"{to_t['date']['y']}-{to_t['date']['m']}-{to_t['date']['d']} {to_t['time']['h']}:{to_t['time']['m']}:{to_t['time']['s']}"

                self.master.comm.send_command(f"DOWNL#{self._signal}#{from_str}#{to_str}#{file_path.name}")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to download data:\n{e}", terminate=True)

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_signals(self, signals: list) -> None:
        self._signals = signals
        try:
            # update option menu
            self._option_menu.destroy()
            self._option_menu = customtkinter.CTkOptionMenu(self._select_frame, values=self._signals, command=self._combo_callback)
            self._option_menu.grid(row=0, column=1, padx=10, pady=5, sticky="nswe")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to update signals:\n{e}", terminate=True)

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

        try:

            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=3)
            self.configure(fg_color="transparent")
            
            # Frame title
            self._title = customtkinter.CTkLabel(self, text="Database configuration", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
            
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
                entry = customtkinter.CTkEntry(self, placeholder_text=self.master.get_config_value("database", name[1]))
                entry.grid(row=i+1, column=1, padx=10, pady=10, sticky="we")

                self._labels.append(label)
                self._entries.append((entry, name[1]))

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - database:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.get_config_value("database", entry[1]))

        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def save_to_json(self) -> bool:
        """Saves database settings changes into the config.json file"""

        for entry in self._entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                if not self.master.update_local_config("database", entry[1], val):
                    return False

        return self.master.write_config_to_file()       


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
            self.grid_columnconfigure(1, weight=3)
            self.configure(fg_color="transparent")

            # Frame title
            self._title = customtkinter.CTkLabel(self, text="Conversion configuration", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
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
                if self.master.get_config_value("settings", name[1]):
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
                entry = customtkinter.CTkEntry(self, placeholder_text=self.master.get_config_value("settings", name[1]))
                entry.grid(row=i+1+len(self._switches), column=1, padx=10, pady=10, sticky="we")

                self._labels.append(label)
                self._entries.append((entry, name[1]))
        
        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - process\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.get_config_value("settings", entry[1]))

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def save_to_json(self) -> bool:
        """Saves process settings changes into the config.json file"""
        # update config
        for switch in self._switches:
            val = int(switch[0].get())
            if val == 1:
                if not self.master.update_local_config("settings", switch[1], True):
                    return False
            if val == 0:
                if not self.master.update_local_config("settings", switch[1], False):
                    return False

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
                if not self.master.update_local_config("settings", entry[1], val):
                    return False

        return self.master.write_config_to_file()


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
            self.configure(corner_radius=0)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)

            # frame title
            self._title = customtkinter.CTkLabel(self, text="Feedback prompt", fg_color="transparent")
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="we")
            
            # define textbox
            self._textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, activate_scrollbars=True, wrap="word")
            self._textbox.grid(row=1, column=0, sticky="nsew")
            self._textbox.configure(state="disabled", font=("Courier New", 12))

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - textbox:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

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

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - progress:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def show(self) -> None:
        """Shows this object inside the master window."""
        try:
            self._title.grid(row=0, column=0, padx=10, pady=0, sticky="w")
            self._progress.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")

        except Exception:
            self.master.error_handle("WARNING", "Unable to show the progress frame", terminate=False)

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def hide(self) -> None:
        """Hides this object within the master window."""
        try:
            self._title.grid_forget()
            self._progress.grid_forget()

        except Exception:
            self.master.error_handle("WARNING", "Unable to hide the progress frame", terminate=False)

        return

# --------------------------------------------------------------------------------------------------------------------------------

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

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - buttons:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_discard(self) -> None:
        """Callback function for the discard button. Opens a new toplevel window."""
        tpe = "WARNING!"
        msge = "All changes you made will not be saved."
        ques = "Do you really want to proceed?"
        self.master.open_toplevel_yn(tpe, msge, ques, self.master.exit_program, self.master.kill_toplevel)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_start(self) -> None:
        """Callback function for the start button."""
        self.master.comm.send_command("RUN-PROP")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_save(self) -> None:
        self.master.save()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_save_start(self) -> None:
        """Callback function for the Save and Start button. Defined via AppInterface."""
        self.master.save()
        self.master.comm.send_command("RUN-PROP")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def disable_buttons(self) -> None:
        """Makes several buttons unclickable"""
        try:
            self._btn_discard.configure(state="disabled")
            self._btn_start.configure(state="disabled")
            self._btn_save_start.configure(state="disabled")

        except Exception:
            self.master.error_handle("WARNING", "Unable to disable buttos", terminate=False)

        return

# --------------------------------------------------------------------------------------------------------------------------------

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


class NavigationFooterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # button manual
        self.btn_manual = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Manual", fg_color="transparent", command=self.btn_callback_manual, text_color=("gray10", "gray90"), anchor="w")
        self.btn_manual.grid(row=0, column=0, padx=0, pady=5, sticky="we")

        # title
        self.label = customtkinter.CTkLabel(self, text="Appearance", fg_color="transparent")
        self.label.grid(row=1, column=0, padx=0, pady=0)

        # appearance mode
        self.appearance = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance.set("System")
        self.appearance.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="we")


    def btn_callback_manual(self) -> None:
        self.master._btn_callback_manual()
        return

    def deselect(self) -> None:
        self.btn_manual.configure(fg_color="transparent")
        return
    
    def select_manual(self) -> None:
        self.btn_manual.configure(fg_color=("gray75", "gray25"))
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def change_appearance_mode(self, mode: str) -> None:
        self.master.change_appearance_mode(mode)
        return 


# ================================================================================================================================


class NavigationFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.btns = []

        # title
        self.label = customtkinter.CTkLabel(self, text="TITLE LOGO", fg_color="transparent")
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # button Before start
        self.btn_before_start = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Before start", fg_color="transparent", command=self._btn_callback_before_start, text_color=("gray10", "gray90"), anchor="w")
        self.btn_before_start.grid(row=1, column=0, sticky="we")
        self.btns.append(self.btn_before_start)

        # button Database config
        self.btn_db_config = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Database config", fg_color="transparent", command=self._btn_callback_db_config, text_color=("gray10", "gray90"), anchor="w")
        self.btn_db_config.grid(row=2, column=0, sticky="we")
        self.btns.append(self.btn_db_config)

        # button Conversion config
        self.btn_conv_config = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Conversion config", fg_color="transparent", command=self._btn_callback_conv_config, text_color=("gray10", "gray90"), anchor="w")
        self.btn_conv_config.grid(row=3, column=0, sticky="we")
        self.btns.append(self.btn_conv_config)

        # button Data download
        self.btn_download = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Download data", fg_color="transparent", command=self._btn_callback_download, text_color=("gray10", "gray90"), anchor="w")
        self.btn_download.grid(row=4, column=0, sticky="we")
        self.btns.append(self.btn_download)

        # footer
        self.footer = NavigationFooterFrame(self)
        self.footer.grid(row=5, column=0, sticky="swe")

# --------------------------------------------------------------------------------------------------------------------------------

    def change_appearance_mode(self, mode: str) -> None:
        self.master.change_appearance_mode(mode)
        return
    
    def set_default(self) -> None:
        self._btn_callback_before_start()
        return
    
    def _btn_callback_before_start(self) -> None:
        self._deselect_btns()
        self.btn_before_start.configure(fg_color=("gray75", "gray25"))
        self.master.load_frame("before-start")
        return
    
    def _btn_callback_db_config(self) -> None:
        self._deselect_btns()
        self.btn_db_config.configure(fg_color=("gray75", "gray25"))
        self.master.load_frame("db-config")
        return
    
    def _btn_callback_conv_config(self) -> None:
        self._deselect_btns()
        self.btn_conv_config.configure(fg_color=("gray75", "gray25"))
        self.master.load_frame("conv-config")
        return
    
    def _btn_callback_download(self) -> None:
        self._deselect_btns()
        self.btn_download.configure(fg_color=("gray75", "gray25"))
        self.master.load_frame("download")
        return
    
    def _btn_callback_manual(self) -> None:
        self._deselect_btns()
        self.footer.select_manual()
        self.master.load_frame("manual")
        return

    def _deselect_btns(self) -> None:
        self.footer.deselect()
        for btn in self.btns:
            btn.configure(fg_color="transparent")

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

        self.comm = None

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
            self.minsize(900, 750)
            self.protocol("WM_DELETE_WINDOW", self._closing_handle)

            # self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # navigation
            self.navigation = NavigationFrame(self)
            self.navigation.grid(row=0, column=0, rowspan=4, sticky="nswe")

            # text box
            self.text_box = TextboxFrame(self)
            self.text_box.grid(row=1, column=1, padx=0, pady=10, sticky="nswe")

            # progress frame
            self.progress_bar = ProgressFrame(self)
            self.progress_bar.grid(row=2, column=1, padx=0, pady=0, sticky="nswe")

            # buttons
            self.button_frame = ButtonsFrame(self)
            self.button_frame.grid(row=3, column=1, padx=5, pady=(10, 15), sticky="nswe")

            # frames
            self.database_frame = DatabaseFrame(self)
            self.process_frame = ProcessFrame(self)
            self.download_frame = DownloadFrame(self)
            self.before_start_frame = BeforeStartFrame(self)

            # display default frame
            self.navigation.set_default()

        except Exception as e:
            print()
            print(f"ERROR while trying to initialize GUI window:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------

    def exit_program(self) -> None:
        self.kill_toplevel()
        self.open_toplevel_exit()
        self.comm.send_command("END")
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def kill_main_window(self) -> None:
        # delay so that popup can load properly
        time.sleep(1)
        self.kill_toplevel()
        self.quit()
        return

# --------------------------------------------------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------------------------------------------------

    def open_toplevel_exit(self) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # create toplevel window
            self.toplevel_window = TopWindowExit(self)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def save(self) -> None:
        """Saves all possible changes into the config.json file."""
        if self.database_frame.save_to_json() and self.process_frame.save_to_json() and self.before_start_frame.save_curr_paths():
            self.text_box.write(f"Successfully saved!\n")
            # update backend configuration
            self.comm.send_command("U-CONF")
        else:
            self.text_box.write(f"Failed to save.\n")

        # redraw 
        self.database_frame.refresh()
        self.process_frame.refresh()

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_local_config(self, domain: str, field: str, content: str) -> bool:
        try:
            self.my_config[domain][field] = content

        except Exception as e:
            self.error_handle("WARNING", f"Problem with updating local settings:\n{e}", False)
            return False
        
        return True

# --------------------------------------------------------------------------------------------------------------------------------

    def write_config_to_file(self) -> bool:
        try:
            with open(os.path.join("src", "config.json"), "w") as file:
                json.dump(self.my_config, file, indent=4)

        except Exception as e:
            self.error_handle("WARNING", f"Problem with writting config to file:\n{e}", False)
            return False
        
        return True

# --------------------------------------------------------------------------------------------------------------------------------

    def get_config_value(self, domain: str, field: str):
        try:
            val = self.my_config[domain][field]

        except Exception as e:
            self.error_handle("WARNING", f"Problem with fetching local settings:\n{e}", False)
            return ""
        
        return val
        
# --------------------------------------------------------------------------------------------------------------------------------

    def set_communication(self, communication) -> None:
        """Sets the connection stream"""
        self.comm = communication
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def kill_toplevel(self) -> None:
        """Destroys the toplevel window"""
        if self.toplevel_window is not None:
            self.toplevel_window.destroy()
            self.toplevel_window.update()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _closing_handle(self) -> None:
        self.open_toplevel_yn("WARNING", "Do you really want to exit?", "", self.exit_program, self.kill_toplevel)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def error_handle(self, type: str, message: str, terminate: bool) -> None:
        """Creates an error popup on demand with the possibility of program termination"""
        if terminate:
            callback = self.exit_program
        else:
            callback = self.kill_toplevel
        
        self.open_toplevel_ok(type, message, callback)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def change_appearance_mode(self, mode: str) -> None:
        customtkinter.set_appearance_mode(mode)
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def get_curr_dir_path(self, path_of: str) -> str:
        try:
            output = self.my_config["settings"][path_of]

        except Exception as e:
            self.error_handle("WARNING", f"Failed to fetch current dir:\n{e}", False)
            return ""
        
        return output

# --------------------------------------------------------------------------------------------------------------------------------

    def load_frame(self, name: str) -> None:
        if name == "before-start":
            self.before_start_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.before_start_frame.grid_forget()

        if name == "db-config":
            self.database_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.database_frame.grid_forget()

        if name == "conv-config":
            self.process_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.process_frame.grid_forget()

        if name == "download":
            self.download_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nswe")
        else:
            self.download_frame.grid_forget()

        if name == "manual":
            pass
        else:
            pass

        return
