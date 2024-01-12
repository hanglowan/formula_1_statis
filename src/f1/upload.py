import pandas as pd

# file_names = ['circuits.csv',
#               'constructor_results.csv',
#               'constructor_standings.csv',
#               'constructors.csv',
#               'driver_standings.csv',
#               'drivers.csv',
#               'lap_times.csv',
#               'pit_stops.csv',
#               'qualifying.csv',
#               'races.csv',
#               'results.csv',
#               'seasons.csv',
#               'sprint_results.csv',
#               'status.csv'
#               ]



drivers = pd.read_csv('../../f1_data/drivers.csv')

# class drivers
from pathlib import Path

my_dir = Path('../../f1_data')
dd = {}
s = str(my_dir)
for file in my_dir.iterdir():
    print(file, type(file))
    print(file.parent, file.name)
    dd[file.name] = pd.read_csv(file)

