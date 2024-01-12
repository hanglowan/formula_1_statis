# import pandas as pd
# from datetime import datetime
# import datetime as dt
# from pathlib import Path
# import os
#
# class Races:
#
#     def get_year_race_ids(self, y:int) -> list:
#         return self.races[self.races.year==y].raceId.to_list()
#
#     def get_driver_race_ids(self, driverId) -> list:
#         return list(set(self.races[self.races.driverId==driverId]['raceId']))
#
#     def get_year(self, raceId):
#         return self.races[self.races.raceId==raceId].year.iloc[0]
#
#     def get_race_circuit_ids(self, raceIds:list, year) -> list:
#         '''race_ids sorted by date descending'''
#        #  print("raceIds:", raceIds)
#        #  print("year:", year)
#         df = self.races[(self.races['raceId'].isin(raceIds)) & (self.races.year==year)]
#         sorted_df = df.sort_values('date', ascending=False)
#         print(sorted_df)
#         sorted_circuits =  list(sorted_df['circuitId'].unique())
#         print("sorted_circuits:", sorted_circuits)
#         return sorted_circuits
#
#     def get_race_circuit_names(self, race_ids, year):
#         df = self.races[(self.races['raceId'].isin(race_ids)) & (self.races.year==year)]
#         sorted_df = df.sort_values('date', ascending=False)
#         print(sorted_df)
#         sorted_circuit_names =  list(sorted_df['name'].unique())
#         print("sorted_circuits_names:", sorted_circuit_names)
#         sorted_circuit_ids =  list(sorted_df['circuitId'].unique())
#         print("sorted_circuits_ids:", sorted_circuit_ids)
#
#         return sorted_circuit_names, sorted_circuit_ids
#
#     # def get_circuit_name(self, circuitId, year):
#     #     return self.races[(self.races.year==year) & (self.races.circuitId==circuitId)].name.iloc[0]
#
#     def get_race_circuit_id(self, raceId:list):
#         return self.races[(self.races['raceId']==(raceId))]['circuitId'].iloc[0]
#
#     def get_race_id(self, year, circuitId):
#         return self.races[(self.races.year==year) & (self.races.circuitId==circuitId)].raceId.iloc[0]
#
