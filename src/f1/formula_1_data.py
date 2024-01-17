import os
import pandas as pd
from f1.driver_data import Drivers
from f1.constructor_data import Ctors
import logging
from pathlib import Path

logger = logging.getLogger(Path(__file__).name)

class Formula_1:
    def __init__(self):
        absolute_path = os.path.dirname(__file__)

        self.drivers = Drivers()

        relative_path = "../../f1_data/drivers.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.driver_info = pd.read_csv(full_path)

        relative_path = "../../f1_data/driver_standings.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.driver_standings = pd.read_csv(full_path)

        relative_path = "../../f1_data/races.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.races = pd.read_csv(full_path)
        self.convert_races()

        relative_path = "../../f1_data/results.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.results = pd.read_csv(full_path)

        relative_path = "../../f1_data/sprint_results.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.sp_results = pd.read_csv(full_path)

        relative_path = "../../f1_data/circuits.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.circuits = pd.read_csv(full_path)

        relative_path = "../../f1_data/lap_times.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.laptimes = pd.read_csv(full_path)

        relative_path = "../../f1_data/pit_stops.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.pitstops = pd.read_csv(full_path)

        relative_path = "../../f1_data/qualifying.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.qualifying = pd.read_csv(full_path)

        relative_path = "../../f1_data/status.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.status = pd.read_csv(full_path)

        self.ctors = Ctors()

        logger.info("init: filter Formula_1")
        self.filter(self.drivers.drivers)
        self.filter(self.races)
        self.filter(self.results)
        self.filter(self.sp_results)
        self.filter(self.circuits)
        # self.filter(self.circuits.gp)
        self.filter(self.qualifying)
        self.filter(self.laptimes)
        self.filter(self.status)
        self.filter(self.pitstops)
        self.filter(self.ctors.ctor_results)
        self.filter(self.ctors.ctors)

    def convert_races(self):
        # convert to datetime
        self.races.date = pd.to_datetime(self.races.date)
        self.races.time = pd.to_datetime(self.races.time, format='%H:%M:%S', errors='coerce')
        cols = self.races.columns[8:17:2]
        self.races[cols] = self.races[cols].apply(pd.to_datetime, format='%Y-%m-%d', errors='coerce')
        cols = self.races.columns[9:18:2]
        self.races[cols] = self.races[cols].apply(pd.to_datetime, format='%H:%M:%S', errors='coerce')

    def filter(self, df:pd.DataFrame):
        for index, col in enumerate(df.columns):
            df[col] = df[col].map(lambda x: '-' if x == "\\N" else x)

    def get_circuit(self, raceId):
        return self.races[self.races.raceId==raceId].circuitId.iloc[0]

    def get_year(self, raceId):
        return self.races[self.races.raceId==raceId].year.iloc[0]

    def get_status(self, sId):
        return self.status[self.status.statusId == sId].status.iloc[0]
    def get_circuit_info(self, circuitId) -> dict:
        if circuitId in self.circuits.gp.columns:
            circuit = self.circuits.gp[self.circuits.gp.circuitId==circuitId]
            return {"laps": circuit.laps.iloc[0],
                    "total_distance": circuit.race_distance.iloc[0],
                    "circuit_length": circuit.circuit_length.iloc[0]}
        else:
            return {"laps": "-",
                    "total_distance": "-",
                    "circuit_length": "-"}

    def get_ctor_id(self, driverId, year, circuit_id):
        logger.info("circuit_id: %s", circuit_id)
        raceId = self.races.get_race_id(year, circuit_id)
        return self.results[(self.results.raceId == raceId) & (self.results.driverId == driverId)].constructorId.iloc[0]

    def get_circuit_name(self, year, circuitId):
        return self.races[(self.races.year == year) & (self.races.circuitId == circuitId)].name.iloc[0]

    def get_year_circuit_ids(self, driverId, year) -> list:
        '''
        returns the circuit ids for the races the driver participated in that year
        :param driverId:
        :param year:
        :return:
        '''
        race_ids = list(self.results[(self.results.driverId == driverId)]['raceId'].unique())

        df = self.races[(self.races['raceId'].isin(race_ids)) & (self.races.year == year)]
        sorted_df = df.sort_values('date', ascending=False)
        sorted_circuits =  list(sorted_df['circuitId'].unique())
        return sorted_circuits

    def get_driver_name(self, driverId):
        '''
        returns the corresponding driver name
        :param driverId:
        :return:
        '''
        return self.drivers.get_driver(driverId)

    def get_circuit_names(self, driverId, year):
        '''
        returns a list of circuit names based on driver participation during a certain year
        :param driverId:
        :param year:
        :return:
        '''
        race_ids = list(self.results[(self.results.driverId == driverId)]['raceId'].unique())

        df = self.races[(self.races['raceId'].isin(race_ids)) & (self.races.year == year)]
        sorted_df = df.sort_values('date', ascending=False)

        circuit_names = list(sorted_df['name'])
        circuit_ids = list(sorted_df['circuitId'])

        return circuit_names, circuit_ids

    def get_range_year_driver_ids(self, years:list):
        '''
        returns all driver ids during a range of years
        :param years:
        :return:
        '''
        race_ids = []
        for year in range(years[0], years[1]+1):
            race_ids.extend(self.races[self.races.year == year].raceId.to_list())
        driver_ids = set()
        for race in race_ids:
            drivers = self.results[self.results.raceId == race].driverId.to_list()
            driver_ids.update(drivers)
        return list(driver_ids)


    def get_year_driver_ids(self, years:list):
        '''
        returns all driver ids during a list of years
        :param years:
        :return:
        '''
        race_ids = []
        for year in years:
            race_ids.extend(self.races[self.races.year == year].raceId.to_list())
        driver_ids = set()
        for race in race_ids:
            drivers = self.results[self.results.raceId == race].driverId.to_list()
            driver_ids.update(drivers)
        return list(driver_ids)

    def get_year_driver_info(self, years:list):
        '''
        returns a Dataframe of drivers during a range of years
        :param years:
        :return:
        '''
        race_ids = []
        for year in range(years[0], years[1]+1):
            race_ids.extend(self.races[self.races.year == year].raceId.to_list())
        driver_ids = set()
        for race in race_ids:
            drivers = self.results[self.results.raceId == race].driverId.to_list()
            driver_ids.update(drivers)
        driver_ids = list(driver_ids)
        return self.drivers.get_rows('driverId', driver_ids)
    @staticmethod
    def display(df:pd.DataFrame):
        if type(df) == 'NoneType':
            logger.info('empty dataframe supplied to Formula_1.display()')
            return
        for index, row in df.iterrows():
            s = []
            for col in df.columns:
                s.append(row[col])
            logger.info("display: %s", s)

    def get_results(self, year):
        race_ids = self.races[self.races.year == year].raceId.tolist()
        race_ids = [race_ids[-1]]
        r23 = self.driver_standings[self.driver_standings.raceId.isin(race_ids)]
        driver_list = r23.driverId.unique().tolist()

        final_standings = []

        for did in driver_list:
            final_standings.append(r23[r23.driverId == did])

        final_standings = pd.concat(final_standings)

        final_standings = final_standings.sort_values(by='points', ascending=False)

        final_standings = pd.merge(final_standings, self.driver_info, on='driverId', how='inner')

        cols = ['position', 'points', 'raceId', 'wins', 'number', 'driverId', 'driverRef', 'code', 'forename',
                'surname', 'url']

        return final_standings.loc[:, cols].copy()



if __name__ == '__main__':
    F1 = Formula_1()
    # print(F1.drivers.drivers.columns)
    # print(F1.races.races.columns)
    print(F1.results.results.columns)
    print(F1.results.sp_results.columns)
