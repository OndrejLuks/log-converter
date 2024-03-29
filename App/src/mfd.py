class MultiFrameDecoder:

    """Class for handling transport protocol data. For each response ID, identify
    sequences of subsequent frames and combine the relevant parts of the data payloads
    into a single payload with the relevant CAN ID. The original raw dataframe is
    then cleansed of the original response ID sequence frames. Instead, the new reassembled
    frames are inserted.

    :param tp_type:                     the class supports UDS ("uds"), NMEA 2000 Fast Packets ("nmea") and J1939 ("j1939")
    :param df_raw:                      dataframe of raw CAN data from the mdf_iter module

    SINGLE_FRAME_MASK:                  mask used in matching single frames
    FIRST_FRAME_MASK:                   mask used in matching first frames
    CONSEQ_FRAME_MASK:                  mask used in matching consequtive frames
    SINGLE_FRAME:                       frame type reflecting a single frame response
    FIRST_FRAME:                        frame type reflecting the first frame in a multi frame response
    CONSEQ_FRAME:                       frame type reflecting a consequtive frame in a multi frame response
    ff_payload_start:                   the combined payload will start at this byte in the FIRST_FRAME
    bam_pgn:                            this is used in J1939 and marks the initial BAM message ID in DEC
    res_id_list:                        TP 'response CAN IDs' to process

    """
    FRAME_STRUCT = {
    "": {},
    "uds": {
        "SINGLE_FRAME_MASK": 0xF0,
        "FIRST_FRAME_MASK": 0xF0,
        "CONSEQ_FRAME_MASK": 0xF0,
        "SINGLE_FRAME": 0x00,
        "FIRST_FRAME": 0x10,
        "CONSEQ_FRAME": 0x20,
        "ff_payload_start": 1,
        "bam_pgn": -1,
        "res_id_list": [1960, 2016, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2026, 1979, 1992, 1998, 2001, 402522235],
        "group": "ID"
    },
    "j1939": {
        "SINGLE_FRAME_MASK": 0xFF,
        "FIRST_FRAME_MASK": 0xFF,
        "CONSEQ_FRAME_MASK": 0x00,
        "SINGLE_FRAME": 0xFF,
        "FIRST_FRAME": 0x20,
        "CONSEQ_FRAME": 0x00,
        "ff_payload_start": 8,
        "bam_pgn": 60416,
        "res_id_list": [60416, 60160],
        "group": "SA"
    },
    "nmea": {
        "SINGLE_FRAME_MASK": 0xFF,
        "FIRST_FRAME_MASK": 0x1F,
        "CONSEQ_FRAME_MASK": 0x00,
        "SINGLE_FRAME": 0xFF,
        "FIRST_FRAME": 0x00,
        "CONSEQ_FRAME": 0x00,
        "ff_payload_start": 2,
        "bam_pgn": -1,
        "res_id_list":[126983, 126984, 126985, 126986, 126987, 126988, 126996, 127233, 127237, 127489, 127496, 127497, 127503, 127504, 127506, 127751, 128275, 128520, 128538, 129029, 129038, 129039, 129040, 129041, 129044, 129284, 129285, 129301, 129302, 129538, 129540, 129541, 129542, 129545, 129547, 129549, 129551, 129556, 129792, 129793, 129794, 129795, 129796, 129798, 129799, 129800, 129801, 129803, 129804, 129805, 129806, 129807, 129808, 129809, 129810, 129811, 129812, 129813, 129814, 129815, 129816, 130052, 130053, 130054, 130060, 130061, 130064, 130065, 130067, 130068, 130069, 130070, 130071, 130072, 130073, 130074, 130320, 130321, 130322, 130323, 130324, 130564, 130565, 130567, 130569, 130571, 130575, 130577, 130578, 130581, 130584, 130586],
        "group": "ID"
}}

    def __init__(self, tp_type=""):
        self.tp_type = tp_type
        return

    def calculate_pgn(self, frame_id):
        pgn = (frame_id & 0x03FFFF00) >> 8
        pgn_f = pgn & 0xFF00
        if pgn_f < 0xF000:
            pgn &= 0xFFFFFF00
        return pgn

    def calculate_sa(self, frame_id):
        sa = frame_id & 0x000000FF
        return sa

    def construct_new_tp_frame(self, base_frame, payload_concatenated, can_id):
        new_frame = base_frame.copy()
        new_frame["DataBytes"] = payload_concatenated
        new_frame["DLC"] = 0
        new_frame["DataLength"] = len(payload_concatenated)
        if can_id:
            new_frame["ID"] = can_id
        return new_frame

    def identify_matching_ids(self,df_raw,res_id_list_full, bam_pgn):
        # identify which CAN IDs (or PGNs) match the TP IDs and create a filtered df_raw_match
        # which is used to separate the df_raw into two parts: Incl/excl TP frames.
        # Also produces a reduced res_id_list that only contains relevant ID entries
        if self.tp_type == "nmea":
            df_raw_pgns = df_raw["ID"].apply(self.calculate_pgn)
            df_raw_match = df_raw_pgns.isin(res_id_list_full)
            res_id_list = df_raw_pgns[df_raw_match].drop_duplicates().values.tolist()
        if self.tp_type == "j1939":
            df_raw_pgns = df_raw["ID"].apply(self.calculate_pgn)
            df_raw_match = df_raw_pgns.isin(res_id_list_full)
            res_id_list = res_id_list_full.copy() 
            res_id_list.remove(bam_pgn)
            if type(res_id_list) is not list:
                res_id_list = [res_id_list]
        elif self.tp_type == "uds":
            df_raw_pgns = None
            df_raw_match = df_raw["ID"].isin(res_id_list_full)
            res_id_list = df_raw["ID"][df_raw_match].drop_duplicates().values.tolist()

        df_raw_tp = df_raw[df_raw_match]
        df_raw_excl_tp = df_raw[~df_raw_match]

        if len(df_raw) - len(df_raw_tp) - len(df_raw_excl_tp):
            print("Warning - total rows does not equal sum of rows incl/excl transport protocol frames")

        return df_raw_tp,  df_raw_excl_tp, res_id_list, df_raw_pgns

    def filter_df_raw_tp(self, df_raw_tp, df_raw_tp_pgns,res_id):
        # filter df_raw_tp to include only frames for the specific response ID res_id
        if self.tp_type == "nmea":
            df_raw_tp_res_id = df_raw_tp[df_raw_tp_pgns.isin([res_id])]
        elif self.tp_type == "j1939":
            df_raw_tp_res_id = df_raw_tp
            df_raw_tp_res_id = df_raw_tp_res_id.copy()
            df_raw_tp_res_id["SA"] = df_raw_tp_res_id["ID"].apply(self.calculate_sa)
        else:
            df_raw_tp_res_id = df_raw_tp[df_raw_tp["ID"].isin([res_id])]
        return df_raw_tp_res_id

    def check_if_first_frame(self,row, bam_pgn, first_frame_mask,first_frame):
        # check if row reflects the first frame of a TP sequence
        if self.tp_type == "j1939" and bam_pgn == self.calculate_pgn(row.ID):
            first_frame_test = True
        elif (row.DataBytes[0] & first_frame_mask) == first_frame:
            first_frame_test = True
        else:
            first_frame_test = False

        return first_frame_test

    def pgn_to_can_id(self,row):
        # for J1939, extract PGN and convert to 29 bit CAN ID for use in baseframe
        pgn_hex = "".join("{:02x}".format(x) for x in reversed(row.DataBytes[5:8]))
        pgn = int(pgn_hex, 16)
        can_id = (6 << 26) | (pgn << 8) | row.SA
        return can_id

    def get_payload_length(self,row):
        if self.tp_type == "uds":
            ff_length = (row.DataBytes[0] & 0x0F) << 8 | row.DataBytes[1]
        if self.tp_type == "nmea":
            ff_length = row.DataBytes[1]
        if self.tp_type == "j1939":
            ff_length = int("".join("{:02x}".format(x) for x in reversed(row.DataBytes[1:2])),16)
        return ff_length

    def combine_tp_frames(self, df_raw):
        # main function that reassembles TP frames in df_raw
        import pandas as pd

        # if tp_type = "" return original df_raw
        if self.tp_type not in ["uds","nmea", "j1939"]:
            return df_raw

        # extract protocol specific TP frame info
        frame_struct = MultiFrameDecoder.FRAME_STRUCT[self.tp_type]
        res_id_list_full = frame_struct["res_id_list"]
        bam_pgn = frame_struct["bam_pgn"]
        ff_payload_start = frame_struct["ff_payload_start"]
        first_frame_mask = frame_struct["FIRST_FRAME_MASK"]
        first_frame = frame_struct["FIRST_FRAME"]
        single_frame_mask = frame_struct["SINGLE_FRAME_MASK"]
        single_frame = frame_struct["SINGLE_FRAME"]
        conseq_frame_mask = frame_struct["CONSEQ_FRAME_MASK"]
        conseq_frame = frame_struct["CONSEQ_FRAME"]

        # split df_raw in two (incl/excl TP frames)
        df_raw_tp,  df_raw_excl_tp, res_id_list, df_raw_pgns = self.identify_matching_ids(df_raw,res_id_list_full, bam_pgn)

        # initiate new df_raw that will contain both the df_raw excl. TP frames and subsequently all combined TP frames
        df_raw = [df_raw_excl_tp]

        # for NMEA, apply PGN decoding outside loop
        if self.tp_type == "nmea":
            df_raw_tp_pgns = df_raw_tp["ID"].apply(self.calculate_pgn)
        else:
            df_raw_tp_pgns = None

        # loop through each relevant TP response ID
        for res_id in res_id_list:

            # get subset of df_raw_tp containing res_id
            df_raw_tp_res_id = self.filter_df_raw_tp(df_raw_tp,df_raw_tp_pgns, res_id)

            # distinguish channels
            for channel, df_channel in df_raw_tp_res_id.groupby("BusChannel"):

                # distinguish IDs from PGNs by grouping on ID (or SA for J1939)
                for identifier, df_raw_filter in df_channel.groupby(frame_struct["group"]):
                    base_frame = df_raw_filter.iloc[0]
                    frame_list = []
                    frame_timestamp_list = []
                    payload_concatenated = []

                    ff_length = 0xFFF
                    first_first_frame_test = True
                    can_id = None
                    conseq_frame_prev = None

                    # iterate through rows in filtered dataframe
                    for row in df_raw_filter.itertuples(index=True,name='Pandas'):
                        index = row.Index
                        first_frame_test = self.check_if_first_frame(row, bam_pgn, first_frame_mask,first_frame)
                        first_byte = row.DataBytes[0]

                        # if single frame, save frame directly (excl. 1st byte)
                        if self.tp_type != "nmea" and (first_byte & single_frame_mask == single_frame):
                            new_frame = self.construct_new_tp_frame(base_frame, row.DataBytes, row.ID)
                            frame_list.append(new_frame.values.tolist())
                            frame_timestamp_list.append(index)

                        # if first frame, save info from prior multi frame response sequence,
                        # then initialize a new sequence incl. the first frame payload
                        elif first_frame_test:
                            # create a new frame using information from previous iterations
                            if len(payload_concatenated) >= ff_length:
                                new_frame = self.construct_new_tp_frame(base_frame, payload_concatenated, can_id)
                                frame_list.append(new_frame.values.tolist())
                                frame_timestamp_list.append(frame_timestamp)

                            # reset and start next frame with timestamp & CAN ID from this first frame plus initial payload
                            conseq_frame_prev = None
                            frame_timestamp = index

                            if self.tp_type == "j1939":
                                can_id = self.pgn_to_can_id(row)

                            ff_length = self.get_payload_length(row)
                            payload_concatenated = row.DataBytes[ff_payload_start:]

                        # if consequtive frame, extend payload with payload excl. 1st byte
                        elif (conseq_frame_prev == None) or ((first_byte - conseq_frame_prev) == 1):
                            conseq_frame_prev = first_byte
                            payload_concatenated += row.DataBytes[1:]


                    df_raw_res_id_new = pd.DataFrame(frame_list, columns=base_frame.index, index=frame_timestamp_list)
                    df_raw.append(df_raw_res_id_new)

        # exclude empty dataframes
        non_empty_df_list = [df for df in df_raw if not df.empty]
        # concat
        df_raw = pd.concat(non_empty_df_list, join='outer')

        df_raw.index.name = "TimeStamp"
        df_raw = df_raw.sort_index()
        return df_raw