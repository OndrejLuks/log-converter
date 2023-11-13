class ProcessData:
    def __init__(self, fs, db_list, signals=[], days_offset=None, verbose=True):
        from datetime import datetime, timedelta

        self.db_list = db_list
        self.signals = signals
        self.fs = fs
        self.days_offset = days_offset
        self.verbose = verbose

        if self.verbose == True and self.days_offset != None:
            date_offset = (datetime.today() - timedelta(days=self.days_offset)).strftime("%Y-%m-%d")
            print(
                f"Warning: days_offset = {self.days_offset}, meaning data is offset to start at {date_offset}.\nThis is intended for sample data testing only. Set days_offset = None when processing your own data."
            )

        return

    def extract_phys(self, df_raw):
        """Given df of raw data and list of decoding databases, create new def with
        physical values (no duplicate signals and optionally filtered/rebaselined)
        """
        import can_decoder
        import pandas as pd

        df_phys = pd.DataFrame()
        df_phys_temp = []
        for db in self.db_list:
            df_decoder = can_decoder.DataFrameDecoder(db)

            for bus, bus_group in df_raw.groupby("BusChannel"):  
                for length, group in bus_group.groupby("DataLength"):
                    df_phys_group = df_decoder.decode_frame(group)
                    if not df_phys_group.empty:
                        df_phys_group["BusChannel"] = bus 
                    df_phys_temp.append(df_phys_group)
                    
        df_phys = pd.concat(df_phys_temp, ignore_index=False).sort_index()
        
        # remove duplicates in case multiple DBC files contain identical signals
        df_phys["datetime"] = df_phys.index
        df_phys = df_phys.drop_duplicates(keep="first")
        df_phys = df_phys.drop(labels="datetime", axis=1)

        # optionally filter and rebaseline the data
        df_phys = self.filter_signals(df_phys)

        if not df_phys.empty and type(self.days_offset) == int:
            df_phys = self.rebaseline_data(df_phys)

        return df_phys

    def rebaseline_data(self, df_phys):
        """Given a df of physical values, this offsets the timestamp
        to be equal to today, minus a given number of days.
        """
        from datetime import datetime, timezone
        import pandas as pd

        delta_days = (datetime.now(timezone.utc) - df_phys.index.min()).days - self.days_offset
        df_phys.index = df_phys.index + pd.Timedelta(delta_days, "day")

        return df_phys

    def filter_signals(self, df_phys):
        """Given a df of physical values, return only signals matched by filter"""
        if not df_phys.empty and len(self.signals):
            df_phys = df_phys[df_phys["Signal"].isin(self.signals)]

        return df_phys

    def get_raw_data(self, log_file, passwords={},lin=False):
        """Extract a df of raw data and device ID from log file.
        Optionally include LIN bus data by setting lin=True
        """
        import mdf_iter

        with self.fs.open(log_file, "rb") as handle:
            mdf_file = mdf_iter.MdfFile(handle, passwords=passwords)
            device_id = self.get_device_id(mdf_file)

            if lin:
                df_raw_lin = mdf_file.get_data_frame_lin()
                df_raw_lin["IDE"] = 0
                df_raw_can = mdf_file.get_data_frame()
                df_raw = df_raw_can.append(df_raw_lin)
            else:
                df_raw = mdf_file.get_data_frame()

        return df_raw, device_id

    def get_device_id(self, mdf_file):
        return mdf_file.get_metadata()["HDcomment.Device Information.serial number"]["value_raw"]

    def print_log_summary(self, device_id, log_file, df_phys):
        """Print summary information for each log file"""
        if self.verbose:
            print(
                "\n---------------",
                f"\nDevice: {device_id} | Log file: {log_file.split(device_id)[-1]} [Extracted {len(df_phys)} decoded frames]\nPeriod: {df_phys.index.min()} - {df_phys.index.max()}\n",
            )