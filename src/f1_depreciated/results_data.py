# import pandas as pd
# from datetime import datetime
# import datetime as dt
# from pathlib import Path
# import os
#
# class Results:
#     def __init__(self):
#         absolute_path = os.path.dirname(__file__)
#         relative_path = "../../f1_data/results.csv"
#         full_path = os.path.join(absolute_path, relative_path)
#         self.results = pd.read_csv(full_path)
#
#         relative_path = "../../f1_data/sprint_results.csv"
#         full_path = os.path.join(absolute_path, relative_path)
#         self.sp_results = pd.read_csv(full_path)
#
#     def get_driver_ids(self, race_ids:list) -> list:
#         driver_ids = set()
#         for race in race_ids:
#             drivers = self.results[self.results.raceId == race].driverId.to_list()
#             driver_ids.update(drivers)
#         return list(driver_ids)
#
#     def get_race_ids(self, driverId):
#         return list(self.results[(self.results.driverId==driverId)]['raceId'].unique())
#
#     def get_sprint_results(self, raceId, driverId) -> list:
#         return self.sp_results[(self.sp_results.raceId==raceId) &
#                                (self.sp_results.driverId==driverId)].values.flatten().tolist()
#
#     def has_sprint(self, raceId) -> bool:
#         return raceId in self.sp_results.raceId.tolist()
#
#     def get_results(self, raceId, driverId) -> list:
#         return self.results[(self.results.raceId==raceId) &
#                             (self.results.driverId==driverId)].values.flatten().tolist()