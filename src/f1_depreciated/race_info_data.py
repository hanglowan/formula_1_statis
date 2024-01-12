# import pandas as pd
# from datetime import datetime
# import datetime as dt
# from pathlib import Path
# import os
#
# class RaceInfo:
#     def __init__(self):
#         absolute_path = os.path.dirname(__file__)
        # relative_path = "../../f1_data/lap_times.csv"
        # full_path = os.path.join(absolute_path, relative_path)
        # self.laptimes = pd.read_csv(full_path)
        # print(self.laptimes.time)
        # self.laptimes.time = pd.to_datetime(self.laptimes.time, format="%M:%S.%f")

        # relative_path = "../../f1_data/pit_stops.csv"
        # full_path = os.path.join(absolute_path, relative_path)
        # self.pitstops = pd.read_csv(full_path)

        # relative_path = "../../f1_data/qualifying.csv"
        # full_path = os.path.join(absolute_path, relative_path)
        # self.qualifying = pd.read_csv(full_path)

        # relative_path = "../../f1_data/status.csv"
        # full_path = os.path.join(absolute_path, relative_path)
        # self.status = pd.read_csv(full_path)

    # def get_status(self, sId):
    #     return self.status[self.status.statusId==sId].status.iloc[0]

    # def get_lap_times(self, driverId, raceId) -> pd.DataFrame:
    #     driver_lt = self.laptimes[(self.laptimes.raceId == raceId) & (self.laptimes.driverId == driverId)]
    #     print(driver_lt.dtypes)
    #     driver_lt["cs_times"] = pd.to_datetime(driver_lt.time).cumsum(axis=None, skipna=True)
    #     return driver_lt

    # def get_pit_stops(self, driverId, raceId) -> pd.DataFrame:
    #     return self.pitstops[(self.pitstops.raceId == raceId) & (self.pitstops.driverId == driverId)]

    # def get_qualify_info(self, driverId, raceId) -> list:
    #     # print(driverId, raceId)
    #     list = self.qualifying[(self.qualifying.raceId == raceId) & (self.qualifying.driverId == driverId)].values.flatten().tolist()
    #     if len(list) == 0:
    #         return ["-"]*9
    #     return list

    # def get_qualify_cols(self) -> list:
    #     return self.qualifying.columns