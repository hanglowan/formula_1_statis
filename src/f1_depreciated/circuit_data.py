# import pandas as pd
# import os
#
# class Circuits:
#     def __init__(self):
#         absolute_path = os.path.dirname(__file__)
#
#
#         relative_path = "../../f1_data/grand_prix.csv"
#         full_path = os.path.join(absolute_path, relative_path)
#         self.gp = pd.read_csv(full_path)
#
#     def get_circuit_names(self, ids:list) -> list:
#         circuit_names = list(self.circuits[self.circuits.circuitId.isin(ids)]['name'].unique())
#         print("circuit_names:", circuit_names)
#         return circuit_names
#
#
#
#     def get_circuit_id(self, circuit_name):
#         print('getting circuit id:', circuit_name)
#         if circuit_name in list(self.gp[circuit_name]):
#             return self.gp[self.gp['circuit'] == circuit_name]['circuitId'].iloc[0]
#         else:
#             return self.circuits[self.circuits['name'] == circuit_name]['circuitId'].iloc[0]
