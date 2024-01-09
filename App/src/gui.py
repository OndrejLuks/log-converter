# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ================================================================================================================================
# ================================================================================================================================

from tkcalendar import Calendar
from tkinter import filedialog
from PIL import Image
import customtkinter
import threading
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
            # disable the [x] closing button
            self.protocol("WM_DELETE_WINDOW", self.closing_handle)

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

# --------------------------------------------------------------------------------------------------------------------------------

    def closing_handle(self) -> None:
        # do nothing means the exit [X] button will be disabled
        return


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
            # disable the [x] closing button
            self.protocol("WM_DELETE_WINDOW", self.closing_handle)
        
            # bring the window into the foregroud
            self.after(100, self.lift)

            # Message
            self._msg = customtkinter.CTkLabel(self, text=msg, fg_color=self.master.col_popup_ok_lab, text_color=self.master.col_popup_ok_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="nswe")

            # OK button
            self._btn_ok = customtkinter.CTkButton(self, text="Okay", text_color=self.master.col_btn_tx, command=callback)
            self._btn_ok.grid(row=1, column=0, padx=10, pady=10, sticky="swe")
        
        except Exception as e:
            self.destroy()
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def closing_handle(self) -> None:
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
            # disable the [x] closing button
            self.protocol("WM_DELETE_WINDOW", self.closing_handle)
        
            # bring the window into the foregroud
            self.after(100, self.lift)

            msg = "Application is closing..."

            # Message
            self._msg = customtkinter.CTkLabel(self, text=msg, fg_color=self.master.col_popup_ok_lab, text_color=self.master.col_popup_ok_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="nswe")
        
        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------

    def closing_handle(self) -> None:
        return


# ================================================================================================================================


class TopWindowEntry(customtkinter.CTkToplevel):
    def __init__(self, master, title: str, message: str, btn_callback_ok: callable, btn_callback_cancel: callable):
        super().__init__(master)

        try:
            self.minsize(300, 150)
            self.resizable(True, False)
            self.title(title)

            self.grid_columnconfigure((0, 1), weight=1)
            
            # bring the window into the foregroud
            self.after(100, self.lift)

            # Message
            self._msg = customtkinter.CTkLabel(self, text=message, fg_color="transparent")
            self._msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 0), sticky="nswe")

            # entry
            self._entry = customtkinter.CTkEntry(self, show="*")
            self._entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nswe")

            # Ok button
            self._btn_yes = customtkinter.CTkButton(self, text="Ok", text_color=self.master.col_btn_tx, command=btn_callback_ok)
            self._btn_yes.grid(row=2, column=0, padx=10, pady=10, sticky="nswe")

            # Cancel button
            self._btn_no = customtkinter.CTkButton(self, text="Cancel", text_color=self.master.col_btn_tx, command=btn_callback_cancel)
            self._btn_no.grid(row=2, column=1, padx=10, pady=10, sticky="nswe")


        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------

    def get_entry_val(self) -> str:
        return self._entry.get()


# ================================================================================================================================

class TopWindowDateTime(customtkinter.CTkToplevel):
    def __init__(self, master, btn_callback_ok: callable, btn_callback_cancel: callable):
        super().__init__(master)

        try:
            self.title("Time filter selector")
            self.minsize(500, 200)
            self.resizable(False, False)
            self.grid_columnconfigure((0, 1), weight=1)

            # bring the window into the foregroud
            self.after(400, self.lift)

            # load image
            self._image = customtkinter.CTkImage(Image.open(os.path.join("src", "media", "date_time_selector.png")), size=(480, 74))

            # Message
            self._msg = customtkinter.CTkLabel(self, text="Select desired dates and type times below", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="nswe")

            # from date-time
            self._date_time_from = DateTimePickerFrame(self, "From:")
            self._date_time_from.grid(row=1, column=0, padx=(5, 10), pady=5, sticky="nswe")

            # to date-time
            self._date_time_to = DateTimePickerFrame(self, "To:")
            self._date_time_to.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="nswe")

            # image
            self._image = customtkinter.CTkLabel(self, text="", image=self._image)
            self._image.grid(row=2, column=0, columnspan=2, padx=0, pady=(5, 15))

            # buttons
            self._btns_frame = customtkinter.CTkFrame(self, corner_radius=0)
            self._btns_frame.grid_columnconfigure((0, 1), weight=1)

            self._btn_yes = customtkinter.CTkButton(self._btns_frame, text="Ok", text_color=self.master.col_btn_tx, command=btn_callback_ok)
            self._btn_yes.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

            self._btn_no = customtkinter.CTkButton(self._btns_frame, text="Cancel", text_color=self.master.col_btn_tx, command=btn_callback_cancel)
            self._btn_no.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

            self._btns_frame.grid(row=3, column=0, columnspan=2, padx=0, pady=0, sticky="swe")

        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------
    
    def get_values(self) -> list:
        return [self._date_time_from.get_values(), self._date_time_to.get_values()]
        

# ================================================================================================================================


class TopWindowSignalSelect(customtkinter.CTkToplevel):
    def __init__(self, master, signals: list, btn_callback_ok: callable, btn_callback_cancel: callable):
        super().__init__(master)

        try:
            self.title("Signal selector")
            self.minsize(400, 500)
            self.resizable(False, True)
            self.grid_columnconfigure((0, 1), weight=1)
            self.grid_rowconfigure(1, weight=1)

            # bring the window into the foregroud
            self.after(100, self.lift)

            self._sig_checkboxes = []

            # Loading
            self._msg = customtkinter.CTkLabel(self, text="Loading...", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="nswe")

            # Signal choices
            self._scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
            self._scrollable_frame.grid_columnconfigure(0, weight=1)
            self._scrollable_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=0, sticky="nswe")

            sig_row_id = 0

            for sig in signals:
                new_checkbox = customtkinter.CTkCheckBox(self._scrollable_frame, text=sig, checkbox_width=20, checkbox_height=20)
                new_checkbox.grid(row=sig_row_id, column=0, padx=10, pady=1, sticky="nsw")
                sig_row_id += 1
                self._sig_checkboxes.append((new_checkbox, sig))

            # buttons
            self._btns_frame = customtkinter.CTkFrame(self, corner_radius=0)
            self._btns_frame.grid_columnconfigure((0, 1), weight=1)

            self._btn_yes = customtkinter.CTkButton(self._btns_frame, text="Ok", text_color=self.master.col_btn_tx, command=btn_callback_ok)
            self._btn_yes.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

            self._btn_no = customtkinter.CTkButton(self._btns_frame, text="Cancel", text_color=self.master.col_btn_tx, command=btn_callback_cancel)
            self._btn_no.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

            self._btns_frame.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="swe")

            # Message
            self._msg.grid_forget()
            self._msg = customtkinter.CTkLabel(self, text="Select desired signals to download", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._msg.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="nswe")

        except Exception as e:
            self.master.text_box.write(f"ERROR While opening toplevel pop-up:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------

    def get_selected_signals(self) -> list:
        output = []

        for box in self._sig_checkboxes:
            if box[0].get() == 1:
                output.append(box[1])

        return output


# ================================================================================================================================


class FolderSelectorFrame(customtkinter.CTkFrame):
    def __init__(self, master, str_label, str_btn, str_current):
        super().__init__(master)

        self._str_label = str_label

        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=5)

        # Selection label
        self._select_label = customtkinter.CTkLabel(self, text=(str_label + ":"), fg_color="transparent")
        self._select_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Selection button
        self._btn = customtkinter.CTkButton(self, text=str_btn, text_color=self.master.master.col_btn_tx, text_color_disabled=self.master.master.col_btn_dis_tx, command=self._btn_callback)
        self._btn.grid(row=0, column=2, padx=10, pady=10, sticky="we")

        # Current folder label
        self._current_label = customtkinter.CTkLabel(self, text=(str_current + ":"), fg_color="transparent")
        self._current_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Current folder selected 
        self._current = customtkinter.CTkEntry(self, placeholder_text="Current directory here")
        self._current.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="we")

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback(self) -> None:
        dir_path = filedialog.askdirectory(title=self._str_label)

        if dir_path:
            self.change_curr_dir(dir_path)
        
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def change_curr_dir(self, new_dir) -> None:
        # clear the entry
        self._current.delete(0, 'end')
        # set new entry
        self._current.insert(0, new_dir)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def get_curr_dir(self) -> str:
        return str(self._current.get())


# ================================================================================================================================


class ManualFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._row_num = 0
        
        # Frame title
        self._title = customtkinter.CTkLabel(self, text="How to use", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
        self._title.grid(row=self._row_num, column=0, padx=10, pady=10, sticky="we")

        self._row_num += 1

        self._scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self._scrollable_frame.grid_columnconfigure(0, weight=1)
        self._scrollable_frame.grid(row=self._row_num, column=0, padx=10, pady=0, sticky="nswe")

        # IMPORTANT INFORMATION
        self._ii_lines = []
        ii_source_notes = [
            "    - Any changes will not be considered unless [Save] or [Save and Start] button is pressed.",
            "    - Loaded text in entry elements represents the current configuration. No need to rewrite it.",
            "    - Some features are available only in ADMIN MODE. Look out for [admin] label in this guide.",
            "    - [Start] button will start the MF4 conversion and upload process"
        ]
        self._h_ii = self._add_heading("IMPORTANT INFORMATION")
        for source_note in ii_source_notes:
            self._ii_lines.append(self._add_note(source_note))

        # Database
        self._db_lines = []
        db_source_notes = [
            "    - Converted signals are automatically loaded into a PostgreSQL database from where Grafana operates.",
            "    - Connection is established based on provided configuration. [admin]",
            "    - Schema will be created or appended according to the name you provide."
        ]
        self._h_db = self._add_heading("Database configuration")
        for source_note in db_source_notes:
            self._db_lines.append(self._add_note(source_note))

        # Conversion
        self._conversion_lines = []
        conversion_source_notes = [
            "    - [Aggregate raw data] option",
            "        - Turns on or off aggregation of raw converted data before upload to the dabatase.",
            "        - Aggregation does not alter original MF4 source files.",
            "        - Aggregation does not alter data values.",
            "        - Aggregation will only remove duplicite entries of same value over time.",
            "    - [Move done files] option",
            "        - Moves processed MF4 files from root directory into the chosen folder.",
            "    - [Write time info into MF4-info.csv] option",
            "        - [admin]",
            "        - Default as true.",
            "        - Extracts first and last time stamp of data record in each MF4 file that is being processed.",
            "    - [Clean database upload] option",
            "        - [admin]",
            "        - Default as false.",
            "        - Deletes given schema from the database with all its contents and creates a new one.",
            "    - [Seconds to skip when value is consistent] entry",
            "        - Visible only if [Aggregate raw data] is selected.",
            "        - Represents maximum amount of seconds of data to remove when aggregating.",
            "        - E. g. if set to 10 and data have duplicite values over more than 10 seconds,",
            "          aggregation will not remove every 10th sec record of those data",
            "    - [Select destination folder for done files] button",
            "        - Visible only if [Move done files] is selected.",
            "        - Sets destination where processed MF4 files will be moved"
        ]
        self._h_conv = self._add_heading("Conversion configuration")
        for source_note in conversion_source_notes:
            self._conversion_lines.append(self._add_note(source_note))

        # Data download
        self._download_lines = []
        download_source_notes = [
            "    - Selected data are fetched right from the database.",
            "    - Multiple signals can be downloaded at once",
            "    - Only CSV format is supported.",
            "    - [Update signal names] button",
            "        - updates internal record of signals stored in the database",
            "    - [Select signals] button",
            "        - lets you pick desired signals to download",
            "    - [Set time filter] button",
            "        - lets you pick time filter for selected signals",
            "    - Both Signals and Time filter must be chosen in order to download"
        ]
        self._h_down = self._add_heading("Data download")
        for source_note in download_source_notes:
            self._download_lines.append(self._add_note(source_note))

# --------------------------------------------------------------------------------------------------------------------------------

    def _add_heading(self, string: str) -> customtkinter.CTkLabel:
        bold_font = customtkinter.CTkFont(weight="bold")
        self._row_num += 1

        new_heading = customtkinter.CTkLabel(self._scrollable_frame, fg_color="transparent", font=bold_font, text=string)
        new_heading.grid(row=self._row_num, column=0, padx=0, pady=(10, 0), sticky="w")
        
        return new_heading

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _add_note(self, string: str) -> customtkinter.CTkLabel:
        self._row_num += 1

        new_note = customtkinter.CTkLabel(self._scrollable_frame, fg_color="transparent", text=string)
        new_note.grid(row=self._row_num, column=0, padx=0, pady=0, sticky="w")

        return new_note


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
        self._mf4_select.change_curr_dir(self.master.get_config_value("settings", "mf4_path"))
        self._mf4_select.grid(row=1, column=0, columnspan=3, padx=0, pady=(0, 40), sticky="we")

        # DBC files
        self._dbc_select = FolderSelectorFrame(self, "Select DBC files root directory", "Select DBC dir", "Current DBC dir")
        self._dbc_select.change_curr_dir(self.master.get_config_value("settings", "dbc_path"))
        self._dbc_select.grid(row=2, column=0, columnspan=3, padx=0, pady=0, sticky="we")
    
# --------------------------------------------------------------------------------------------------------------------------------

    def save_locally(self) -> bool:
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
        
        return True
    

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

            # hours
            hh = customtkinter.CTkEntry(self, placeholder_text="hh", width=self._entry_width)
            hh.grid(row=0, column=0, padx=0, pady=0, sticky="nswe")
            self._entries.append(hh)
            # :
            self._col1 = customtkinter.CTkLabel(self, text=":", fg_color="transparent")
            self._col1.grid(row=0, column=1, padx=5, pady=0, sticky="nswe")
            # minutes
            mm = customtkinter.CTkEntry(self, placeholder_text="mm", width=self._entry_width)
            mm.grid(row=0, column=2, padx=0, pady=0, sticky="nswe")
            self._entries.append(mm)
            # :
            self._col2 = customtkinter.CTkLabel(self, text=":", fg_color="transparent")
            self._col2.grid(row=0, column=3, padx=5, pady=0, sticky="nswe")
            # seconds
            ss = customtkinter.CTkEntry(self, placeholder_text="ss", width=self._entry_width)
            ss.grid(row=0, column=4, padx=0, pady=0, sticky="nswe")
            self._entries.append(ss)

        except Exception as e:
            self.master.master.master.error_handle("ERROR", f"Unable to create GUI - time entry:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------
    
    def get_values(self) -> list:
        output = []

        for entry in self._entries:
            val = str(entry.get())
            if not len(val) == 0:
                output.append(val)
            else:
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
            self._time_select_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="nsw")

            # callendar
            self._calendar = Calendar(self, selectmode="day", locale="en", showweeknumbers=False, cursor="hand2", date_pattern="y-mm-dd", borderwidth=0, bordercolor="white")
            self._calendar.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="we")

            # time
            self._time_entry = TimeSelectorFrame(self)
            self._time_entry.grid(row=2, column=0, padx=10, pady=(5,10), sticky="we")
        
        except Exception as e:
            self.master.master.error_handle("ERROR", f"Unable to create GUI - date entry:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def get_values(self) -> dict:
        try:
            time_val = self._time_entry.get_values()
            date_val = self._calendar.get_date().split("-")
            # format output into a dictionary
            output = {"date" : {"y" : date_val[0], "m" : date_val[1], "d" : date_val[2]},
                      "time" : {"h" : time_val[0], "m" : time_val[1], "s" : time_val[2]}}
            
        except Exception as e:
            self.master.master.error_handle("ERROR", f"Problem with fetching date and time:\n{e}", terminate=True)
            return None

        return output


# ================================================================================================================================


class DownloadFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(6, weight=1)
            self.configure(fg_color="transparent")

            self._selected_signals = []
            self._from_str = ""
            self._to_str = ""
            self._signals = ["none"]

            # frame title
            self._title = customtkinter.CTkLabel(self, text="Data download", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")

            # label signal load
            self._label_btn_load = customtkinter.CTkLabel(self, text="1)  Update current signal names")
            self._label_btn_load.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsw")

            # btn signal load
            self._btn_load = customtkinter.CTkButton(self, text="Update signal names", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_load, width=200)
            self._btn_load.grid(row=1, column=1, padx=10, pady=(10, 5), sticky="nse")

            # label signal select
            self._label_btn_select = customtkinter.CTkLabel(self, text="2)  Select signals to download")
            self._label_btn_select.grid(row=2, column=0, padx=10, pady=5, sticky="nsw")

            # btn signal selection
            self._btn_select_signals = customtkinter.CTkButton(self, text="Select signals", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_select_sig, width=200)
            self._btn_select_signals.grid(row=2, column=1, padx=10, pady=5, sticky="nse")
            self._btn_select_signals.configure(state="disabled")

            # label time filter
            self._label_btn_time_filter = customtkinter.CTkLabel(self, text="3)  Select time range of downloaded data")
            self._label_btn_time_filter.grid(row=3, column=0, padx=10, pady=5, sticky="nsw")

            # btn select time filter
            self._btn_time_filter = customtkinter.CTkButton(self, text="Set time filter", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_time_filter, width=200)
            self._btn_time_filter.grid(row=3, column=1, padx=10, pady=5, sticky="nse")
            self._btn_time_filter.configure(state="disabled")

            # textbox label
            self._label_txtbox = customtkinter.CTkLabel(self, text="Current selection for download:", fg_color="transparent")
            self._label_txtbox.grid(row=4, column=0, columnspan=2, padx=10, pady=(20, 2), sticky="we")
            
            # textbox
            self._textbox = customtkinter.CTkTextbox(self, activate_scrollbars=True, wrap="word", height=100)
            self._textbox.grid(row=5, column=0, columnspan=2, padx=50, pady=0, sticky="nsew")
            self._textbox.configure(state="disabled", font=("Courier New", 12))

            # download button
            self._btn_download = customtkinter.CTkButton(self, text="Download as csv", text_color=self.master.col_btn_tx, text_color_disabled=self.master.col_btn_dis_tx, command=self._btn_callback_download, width=200)
            self._btn_download.grid(row=6, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="s")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - download:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_load(self) -> None:
        self._signals.clear()
        # fetch signals from the database
        self.master.comm.send_command("FETCH-SIG")
        # print current selection (will be blank)
        self._print_current_selection()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_time_filter(self) -> None:
        # open a pop-up with datetime selection
        self.master.open_toplevel_date_time(self._time_filter_update)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _time_filter_update(self) -> None:
        if isinstance(self.master.toplevel_window, TopWindowDateTime):
            # fetch datetime values and kill the pop-up
            time_values = self.master.toplevel_window.get_values()
            self.master.kill_toplevel()

            if time_values[0] and time_values[1]:
                from_t = time_values[0]
                to_t = time_values[1]

                # format "yyyy-mm-dd hh-ss-mm"
                self._from_str = f"{from_t['date']['y']}-{from_t['date']['m']}-{from_t['date']['d']} {from_t['time']['h']}:{from_t['time']['m']}:{from_t['time']['s']}"
                self._to_str = f"{to_t['date']['y']}-{to_t['date']['m']}-{to_t['date']['d']} {to_t['time']['h']}:{to_t['time']['m']}:{to_t['time']['s']}"

                # print current selection
                self._print_current_selection()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _selected_signals_update(self) -> None:
        if isinstance(self.master.toplevel_window, TopWindowSignalSelect):
            # get selected signals
            self._selected_signals = self.master.toplevel_window.get_selected_signals()
            self.master.kill_toplevel()

            # print current selection
            self._print_current_selection()
        
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_select_sig(self) -> None:
        # open a new thread with signal selection
        self.master.spawn_working_thread(fc=self.master.open_toplevel_signal_select, args=(self._signals, self._selected_signals_update))
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_download(self) -> None:
        if len(self._selected_signals) == 0:
            self.master.error_handle("WARNING", "Signal not selected!", False)
            return
        
        if self._from_str == "" or self._to_str == "":
            self.master.error_handle("WARNING", "Time filter not selected!", False)
            return

        try:
            # ask for destination to save the file
            file_path = filedialog.asksaveasfile(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            # file path was provided
            if file_path:
                # merge signals into semicolumn-separated string
                signals_str = ""
                for idx, sig in enumerate(self._selected_signals):
                    signals_str = signals_str + sig
                    if idx < len(self._selected_signals) - 1:
                        signals_str = signals_str + ";"

                # send string command
                self.master.comm.send_command(f"DOWNL#{signals_str}#{self._from_str}#{self._to_str}#{file_path.name}")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to download data:\n{e}", terminate=True)

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_signals(self, signals: list) -> None:
        # called from the interface
        self._signals = signals
        try:
            # enable buttons
            self._btn_select_signals.configure(state="normal")
            self._btn_time_filter.configure(state="normal")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to update signals:\n{e}", terminate=True)

        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def _print_current_selection(self) -> None:
        # make the textbox writeable
        self._textbox.configure(state="normal")
        # clear contents
        self._textbox.delete("0.0", "end")
        # insert message at the end
        self._textbox.insert("end", "Selected signals:\n")

        for idx, sig in enumerate(self._selected_signals):
            self._textbox.insert("end", sig)
            if idx < len(self._selected_signals) - 1:
                self._textbox.insert("end", ", ")

        self._textbox.insert("end", "\n\n")

        self._textbox.insert("end", "Selected time filters:")
        self._textbox.insert("end", f"   FROM: {self._from_str}\n")
        self._textbox.insert("end", f"                         TO:   {self._to_str}\n")

        # make the textbox non-writeable
        self._textbox.configure(state="disabled")
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
            self.grid_columnconfigure(1, weight=4)
            self.configure(fg_color="transparent")
            
            # Frame title
            self._title = customtkinter.CTkLabel(self, text="Database configuration", fg_color=self.master.col_frame_title_bg, text_color=self.master.col_frame_title_tx, corner_radius=6)
            self._title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="we")
            
            # define entry names and their permissions
            self.entry_names = [("Host", "host", "admin"),
                        ("Port", "port", "admin"),
                        ("Database", "database", "admin"),
                        ("User", "user", "admin"),
                        ("Password", "password", "admin"),
                        ("Schema", "schema_name", "user")]
            self._entries = []

            # create entries
            for i, name in enumerate(self.entry_names):
                label = customtkinter.CTkLabel(self, text=name[0], fg_color="transparent")
                entry = customtkinter.CTkEntry(self, placeholder_text=self.master.get_config_value("database", name[1]))
                self._entries.append((entry, name[1]))

                if name[2] == "admin" and not self.master.admin_mode:
                    # don't display created entry if it requires admin permission
                    continue

                label.grid(row=i+1, column=0, padx=15, pady=10, sticky="w")
                entry.grid(row=i+1, column=1, padx=10, pady=10, sticky="we")

        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - database:\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.get_config_value("database", entry[1]))

        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def save_locally(self) -> bool:
        """Saves database settings changes into the config file in memory"""

        for entry in self._entries:
            val = str(entry[0].get())
            if not len(val) == 0:
                if not self.master.update_local_config("database", entry[1], val):
                    return False

        return True


# ================================================================================================================================   


class ConversionFrame(customtkinter.CTkFrame):
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

            # create and show switches
            self._switches = []
            self._swch_aggregate = self._create_switch(1, 0, "Aggregate raw data", ("settings", "aggregate"), self._agg_seconds_grid)
            self._swch_move = self._create_switch(2, 0, "Move done files", ("settings", "move_done_files"), self._move_done_dest_grid)
            
            if self.master.admin_mode:
                # show these only if admin mode is on
                self._swch_write_info = self._create_switch(3, 0, "Write time info into MF4-info.csv", ("settings", "write_time_info"))
                self._swch_clean_up = self._create_switch(4, 0, "Clean database upload", ("settings", "clean_upload"))

            # create and show entries
            self._entries = []
            self._entry_agg_frame = self._create_entry(5, 0, "Seconds to skip when value is consistent", ("settings", "agg_max_skip_seconds"))

            # ask for done destination
            self._done_dest_select = FolderSelectorFrame(self, "Select destination folder for done files", "Select destination", "Current destination")
            self._done_dest_select.change_curr_dir(self.master.get_config_value("settings", "done_path"))

            # display additional frames according to current settings
            self._agg_seconds_grid()
            self._move_done_dest_grid()
        
        except Exception as e:
            self.master.error_handle("ERROR", f"Unable to create GUI - process\n{e}", terminate=True)

# --------------------------------------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Updates dynamic elements of the GUI based on config.json content."""
        for entry in self._entries:
            entry[0].configure(placeholder_text=self.master.get_config_value(entry[1][0], entry[1][1]))

        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def _agg_seconds_grid(self) -> None:
        # aggregation seconds skip is displayed only if aggregation switch is on
        val = self._swch_aggregate.get()

        if val == 1:
            self._entry_agg_frame[0].grid(row=self._entry_agg_frame[1][0], column=self._entry_agg_frame[1][1], padx=0, pady=0, sticky="we")

        if val == 0:
            self._entry_agg_frame[0].grid_forget()
        
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _move_done_dest_grid(self) -> None:
        # move to destinaton selection is displayed only if move switch is on
        val = self._swch_move.get()

        if val == 1:
            self._done_dest_select.grid(row=6, column=0, columnspan=3, padx=0, pady=(20, 40), sticky="we")

        if val == 0:
            self._done_dest_select.grid_forget()
        
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _create_switch(self, r_id: int, col_id: int, label: str, config: tuple, callback: callable = None) -> customtkinter.CTkSwitch:
        new_switch = customtkinter.CTkSwitch(self, text=label, command=callback)
        new_switch.grid(row=r_id, column=col_id, columnspan=2, padx=10, pady=10, sticky="w")

        # saving switch in a tuple together with config (also a tuple)
        self._switches.append((new_switch, config))
        if self.master.get_config_value(config[0], config[1]) == "true":
            new_switch.select()

        return new_switch
    
# --------------------------------------------------------------------------------------------------------------------------------

    def _create_entry(self, r_id: int, col_id: int, label: str, config: tuple) -> tuple:
        entry_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        entry_frame.grid_columnconfigure(0, weight=1)
        entry_frame.grid_columnconfigure(1, weight=3)

        en_label = customtkinter.CTkLabel(entry_frame, text=label, fg_color="transparent")
        en_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        new_entry = customtkinter.CTkEntry(entry_frame, placeholder_text=self.master.get_config_value(config[0], config[1]))
        new_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        # saving entry in a tuple together with config (also a tuple)
        self._entries.append((new_entry, config))

        return (entry_frame, (r_id, col_id))

# --------------------------------------------------------------------------------------------------------------------------------

    def save_locally(self) -> bool:
        """Saves process settings changes into the config file in memory"""
        # update local config - current status of switches 
        for switch in self._switches:
            val = int(switch[0].get())
            if val == 1:
                if not self.master.update_local_config(switch[1][0], switch[1][1], "true"):
                    return False
            if val == 0:
                if not self.master.update_local_config(switch[1][0], switch[1][1], "false"):
                    return False

        # update local config - current status of entries
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
                if not self.master.update_local_config(entry[1][0], entry[1][1], val):
                    return False
        
        # save move to destination if move switch is on
        if self._swch_move.get() == 1:
            done_dest_dir = self._done_dest_select.get_curr_dir()

            if len(done_dest_dir) == 0:
                self.master.error_handle("WARNING", "Destination for done files not selected!", False)
                return False
            
            if not self.master.update_local_config("settings", "done_path", done_dest_dir):
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
        with self.master.thr_lock:
            # make the textbox writeable
            self._textbox.configure(state="normal")
            # insert message at the end
            self._textbox.insert("end", msg)
            # scroll to the end
            self._textbox.see("end")
            # make the textbox non-writeable
            self._textbox.configure(state="disabled")
        return
    
# --------------------------------------------------------------------------------------------------------------------------------
    
    def clear(self) -> None:
        self._textbox.configure(state="normal")
        self._textbox.delete("0.0", "end")
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
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # load media
        self._ic_help = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-hlp-l.png")),
                                        dark_image=Image.open(os.path.join("src", "media", "ic-hlp-d.png")), size=(20, 20))
        self._ic_admin = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-adm-l.png")),
                                        dark_image=Image.open(os.path.join("src", "media", "ic-adm-d.png")), size=(20, 20))

        # button manual
        self.btn_manual = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Manual", fg_color="transparent", command=self.btn_callback_manual, text_color=("gray10", "gray90"), anchor="w", image=self._ic_help)
        self.btn_manual.grid(row=0, column=0, columnspan=2, sticky="we")

        # button enable admin mode
        self.btn_admin = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Admin mode", fg_color="transparent", command=self.btn_callback_admin, text_color=("gray10", "gray90"), anchor="w", image=self._ic_admin)
        self.btn_admin.grid(row=1, column=0, pady=(0, 5), columnspan=2, sticky="we")

        # appearance mode title
        self.label = customtkinter.CTkLabel(self, text="Theme", fg_color="transparent")
        self.label.grid(row=2, column=0, padx=(15, 10), pady=(5, 20), sticky="w")

        # appearance mode selection
        self.appearance = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance.set("System")
        self.appearance.grid(row=2, column=1, padx=(0, 20), pady=(5, 20), sticky="w")

# --------------------------------------------------------------------------------------------------------------------------------

    def btn_callback_manual(self) -> None:
        self.master._btn_callback_manual()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def btn_callback_admin(self) -> None:
        self.master._btn_callback_admin()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def deselect(self) -> None:
        self.btn_manual.configure(fg_color="transparent")
        self.btn_admin.configure(fg_color="transparent")
        return
    
# --------------------------------------------------------------------------------------------------------------------------------
    
    def select_manual(self) -> None:
        self.btn_manual.configure(fg_color=("gray75", "gray25"))
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def change_appearance_mode(self, mode: str) -> None:
        self.master.change_appearance_mode(mode)
        return 
    
# --------------------------------------------------------------------------------------------------------------------------------

    def disable_admin(self) -> None:
        self.btn_admin.configure(state="disabled")
        return


# ================================================================================================================================


class NavigationFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.btns = []

        # define colors
        self.col_btn_tx = self.master.col_btn_tx

        # load media
        self._logo = customtkinter.CTkImage(Image.open(os.path.join("src", "media", "logo.png")), size=(226, 170))
        self._ic_before_start = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-st-l.png")),
                                                       dark_image=Image.open(os.path.join("src", "media", "ic-st-d.png")), size=(20, 20))
        self._ic_db = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-db-l.png")),
                                             dark_image=Image.open(os.path.join("src", "media", "ic-db-d.png")), size=(20, 20))
        self._ic_conv = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-conv-l.png")),
                                               dark_image=Image.open(os.path.join("src", "media", "ic-conv-d.png")), size=(20, 20))
        self._ic_download = customtkinter.CTkImage(light_image=Image.open(os.path.join("src", "media", "ic-dwn-l.png")),
                                                   dark_image=Image.open(os.path.join("src", "media", "ic-dwn-d.png")), size=(20, 20))

        # header logo
        self.label = customtkinter.CTkLabel(self, text="", image=self._logo)
        self.label.grid(row=0, column=0, padx=0, pady=0)

        # button Before start
        self.btn_before_start = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Before start", fg_color="transparent", command=self._btn_callback_before_start, text_color=("gray10", "gray90"), anchor="w", image=self._ic_before_start)
        self.btn_before_start.grid(row=1, column=0, sticky="we")
        self.btns.append(self.btn_before_start)

        # button Database config
        self.btn_db_config = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Database config", fg_color="transparent", command=self._btn_callback_db_config, text_color=("gray10", "gray90"), anchor="w", image=self._ic_db)
        self.btn_db_config.grid(row=2, column=0, sticky="we")
        self.btns.append(self.btn_db_config)

        # button Conversion config
        self.btn_conv_config = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Conversion config", fg_color="transparent", command=self._btn_callback_conv_config, text_color=("gray10", "gray90"), anchor="w", image=self._ic_conv)
        self.btn_conv_config.grid(row=3, column=0, sticky="we")
        self.btns.append(self.btn_conv_config)

        # button Data download
        self.btn_download = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Download data", fg_color="transparent", command=self._btn_callback_download, text_color=("gray10", "gray90"), anchor="w", image=self._ic_download)
        self.btn_download.grid(row=4, column=0, sticky="we")
        self.btns.append(self.btn_download)

        # footer
        self.footer = NavigationFooterFrame(self)
        self.footer.grid(row=5, column=0, sticky="swe")

# --------------------------------------------------------------------------------------------------------------------------------

    def change_appearance_mode(self, mode: str) -> None:
        self.master.change_appearance_mode(mode)
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def set_default(self) -> None:
        # default frame is set to be te first one - Before Start
        self._btn_callback_before_start()
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback_before_start(self) -> None:
        self._deselect_btns()
        # visually select before start button
        self.btn_before_start.configure(fg_color=("gray75", "gray25"))
        # load before start frame
        self.master.load_frame("before-start")
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback_db_config(self) -> None:
        self._deselect_btns()
        # visually select database config button
        self.btn_db_config.configure(fg_color=("gray75", "gray25"))
        # load database config frame
        self.master.load_frame("db-config")
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback_conv_config(self) -> None:
        self._deselect_btns()
        # visually select conversion config button
        self.btn_conv_config.configure(fg_color=("gray75", "gray25"))
        # load conversion config frame
        self.master.load_frame("conv-config")
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback_download(self) -> None:
        self._deselect_btns()
        # visually select download button
        self.btn_download.configure(fg_color=("gray75", "gray25"))
        # load download frame
        self.master.load_frame("download")
        return

# --------------------------------------------------------------------------------------------------------------------------------
    
    def _btn_callback_manual(self) -> None:
        self._deselect_btns()
        # visually select manual button
        self.footer.select_manual()
        # load manual frame
        self.master.load_frame("manual")
        return
    
# --------------------------------------------------------------------------------------------------------------------------------

    def _btn_callback_admin(self) -> None:
        # prompt for password and pass admin handle function
        self.master.open_toplevel_entry("Enter the password", "Enter the admin password below:", self.master.handle_admin_mode)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def disable_admin(self) -> None:
        # disables admin mode button
        self.footer.disable_admin()
        return

# --------------------------------------------------------------------------------------------------------------------------------

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
    - toplevel_window
    - database_frame : DatabaseFrame
    - conversion_frame : ConversionFrame
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
        self.toplevel_window = None
        self.curr_conf_val = None
        self.thr_event = None
        self.admin_mode = False
        self.threads = []
        self.thr_lock = threading.Lock()

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

            self.title("BobLoader MF4")
            self.iconbitmap(os.path.join("src", "media", "icon-logo.ico"))
            self.minsize(900, 750)
            self.protocol("WM_DELETE_WINDOW", self._closing_handle)

            # self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Loading ... label
            self._load_label = customtkinter.CTkLabel(self, text="Loading...", fg_color="transparent")
            self._load_label.grid(row=0, column=1, padx=10, pady=50, sticky="nwe")

        except Exception as e:
            print()
            print(f"ERROR while trying to initialize main GUI window:\n{e}")

# --------------------------------------------------------------------------------------------------------------------------------

    def spawn_working_thread(self, fc: callable, args: set=()) -> None:
        # spawns a new thread with assigned function
        new_thr = threading.Thread(target=fc, args=args)
        new_thr.start()
        self.threads.append(new_thr)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def join_threads(self) -> None:
        for thr in self.threads:
            if thr.is_alive():
                thr.join()

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def exit_program(self) -> None:
        self.kill_toplevel()
        self.open_toplevel_exit()
        self.join_threads()
        self.comm.send_command("END")
        return

# --------------------------------------------------------------------------------------------------------------------------------    

    def set_communication(self, communication) -> None:
        self.comm = communication
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def kill_main_window(self) -> None:
        # delay so that popup can load properly
        time.sleep(1)
        self.kill_toplevel()
        self.quit()
        return

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

    def open_toplevel_entry(self, title: str, message: str, callback_ok: callable, callback_cancel: callable = None) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # assign toplevel kill if cancel callback is not specified
            if callback_cancel == None:
                callback_cancel = self.kill_toplevel

            # create toplevel window
            self.toplevel_window = TopWindowEntry(self, title, message, callback_ok, callback_cancel)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def open_toplevel_date_time(self, callback_ok: callable, callback_cancel: callable = None) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # assign toplevel kill if cancel callback is not specified
            if callback_cancel == None:
                callback_cancel = self.kill_toplevel

            # create toplevel window
            self.toplevel_window = TopWindowDateTime(self, callback_ok, callback_cancel)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def open_toplevel_signal_select(self, signals: list, callback_ok: callable, callback_cancel: callable = None) -> None:
        # check for window existance
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # assign toplevel kill if cancel callback is not specified
            if callback_cancel == None:
                callback_cancel = self.kill_toplevel

            # create toplevel window
            self.toplevel_window = TopWindowSignalSelect(self, signals, callback_ok, callback_cancel)
            # position the toplevel window relatively to the main window
            self.toplevel_window.geometry("+%d+%d" %(self.winfo_x()+200, self.winfo_y()+200))

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def handle_admin_mode(self) -> None:
        if isinstance(self.toplevel_window, TopWindowEntry):
            # get user typed password
            entered_pswd = self.toplevel_window.get_entry_val()
            
            # get correct password
            correct_pswd = self.get_config_value("settings", "admin_pswd")
           
            if correct_pswd == entered_pswd:
                self.admin_mode = True
                self.text_box.write("Successfully switched to ADMIN MODE.\n")
                self.title(f"{self.title()} - ADMIN MODE")
                self.navigation.disable_admin()

                # reset database frame and conversion frame, so that values are updated
                self.database_frame = DatabaseFrame(self)
                self.conversion_frame = ConversionFrame(self)
                # change current view to startup screen
                self.navigation.set_default()

            else:
                self.text_box.write("\n!!! Incorrect password.\n")
        
        self.kill_toplevel()
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def save(self) -> None:
        self.spawn_working_thread(fc=self._save)
        return

# --------------------------------------------------------------------------------------------------------------------------------

    def _save(self) -> None:
        # 1st: update local configs
        #   - several methods to each objects

        if not (self.database_frame.save_locally() and self.conversion_frame.save_locally() and self.before_start_frame.save_locally()):
            self.text_box.write("Failed to update local settings.\n")
            return

        # 2nd: flush settings to the file
        #   - take local settings file and flush it

        if not self.flush_config_to_file():
            self.text_box.write("Failed to write settings to the file.\n")
            return

        # 3rd: redraw
        self.database_frame.refresh()
        self.conversion_frame.refresh()

        return

# --------------------------------------------------------------------------------------------------------------------------------

    def update_local_config(self, domain: str, field: str, content: str) -> bool:
        
        # Update local sends particular parametres to backend and updates local backend config
        
        try:
            self.comm.send_command(f"U-CONF#{domain}#{field}#{content}")

        except Exception as e:
            self.error_handle("WARNING", f"Problem with requesting of updating local settings:\n{e}", False)
            return False
        
        return True

# --------------------------------------------------------------------------------------------------------------------------------

    def flush_config_to_file(self) -> bool:

        # write config to file sends command to backend to dump config into file

        try:
            self.comm.send_command("FLUSH-CONF")

        except Exception as e:
            self.error_handle("WARNING", f"Problem with requesting of writting config to file:\n{e}", False)
            return False
        
        return True

# --------------------------------------------------------------------------------------------------------------------------------

    def get_config_value(self, domain: str, field: str) -> str:
        value = ""

        try:
            # fetching config values from config file stored in backend
            self.comm.send_command(f"FETCH-CONF#{domain}#{field}")

            # wait for a flag that the new value is really fetched
            self.thr_event.wait(timeout=3)
            self.thr_event.clear()

            # backend function writes fetched value into self.corr_conf_val

            value = self.curr_conf_val
            self.curr_conf_val = None

        except Exception as e:
            self.error_handle("WARNING", f"Problem with requesting of fetching local settings:\n{e}", False)
            return ""

        return value

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
            self.conversion_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.conversion_frame.grid_forget()

        if name == "download":
            self.download_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.download_frame.grid_forget()

        if name == "manual":
            self.manual_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nswe")
        else:
            self.manual_frame.grid_forget()

        return
    

    def init(self) -> None:
        try:
            # remove loading label
            self._load_label.grid_forget()

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
            self.conversion_frame = ConversionFrame(self)
            self.download_frame = DownloadFrame(self)
            self.before_start_frame = BeforeStartFrame(self)
            self.manual_frame = ManualFrame(self)

            # display default frame
            self.navigation.set_default()

        except Exception as e:
            self.error_handle("ERROR", f"Failed to initialize gui frames:\n{e}", True)
        
        return
    
