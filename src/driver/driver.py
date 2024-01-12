import pandas as pd
import datetime
from fastf1.ergast import Ergast
from f1.formula_1_data import Formula_1
from f1.driver_data import Drivers
import logging
from pathlib import Path

logger = logging.getLogger(Path(__file__).name)

epoch = datetime.datetime.utcfromtimestamp(0)


class Driver:

    @staticmethod
    def get_driver_id(code):
        drivers = Drivers()
        return drivers.get_driver_id(code)

    def __init__(self, driverId=None) -> None:
        if driverId==None:
            return
        self.f1 = Formula_1()
        self.ergast = Ergast()
        self.driverId = driverId
        self.name = self.f1.drivers.get_driver(driverId)
        logger.info("initalize driver: %s, %s", self.driverId, self.name)

    def basic_info(self) -> str:
        return str(self.driverId) + ": " + self.name

    def all_info(self) -> dict:
        logger.info("call: Driver.all_info")
        info = dict()
        cols = self.f1.drivers.get_columns()
        for index, elem in enumerate(self.f1.drivers.get_info(self.driverId)):
            info.update({cols[index]:elem})
        return info
    
    def get_final_results(self, year, code):
        df = self.ergast.get_driver_standings(year).content[0]
        return df[df.driverCode==code]

    def constructor_id(self, year, circuitId):
        logger.info("call: Driver.constructor_id")
        return self.f1.get_ctor_id(self.driverId, year, circuitId)

    def get_ctor_nation(self, year, circuitId):
        ctor_id = self.constructor_id(year, circuitId)
        return self.f1.ctors.get_constructor_nationality(ctor_id)

    def years_participated(self):
        race_ids = list(self.f1.results[(self.f1.results.driverId == self.driverId)]['raceId'].unique())
        years = self.f1.races[self.f1.races['raceId'].isin(race_ids)].year.tolist()
        years = list(set(years))
        years.sort(reverse=True)
        return years

    def get_last_year(self):
        years = self.years_participated()
        return years[0]

    def get_last_circuit(self):
        year = self.get_last_year()
        circuit_names, circuit_ids = self.f1.get_circuit_names(self.driverId, year)
        circuit_name = circuit_names[0]
        return circuit_name

    def get_circuit_names_ids(self, season):
        circuit_names, circuit_ids = self.f1.get_circuit_names(self.driverId, season)

        return circuit_names, circuit_ids

    def circuit_ids(self, year) -> list:
        logger.info("call: Driver.circuit_ids")
        return self.f1.get_year_circuit_ids(self.driverId, year)

    def race_id(self, year, circuit_id):
        logger.info("race_id: %s, %s", year, circuit_id)
        return self.f1.races[(self.f1.races.year == year) & (self.f1.races.circuitId == circuit_id)].raceId.iloc[0]

    def sp_results(self, year, circuit_id) -> dict:
        logger.info("%s, %s", year, circuit_id)
        raceId = self.race_id(year, circuit_id)
        sprint_results_list = self.f1.sp_results[(self.f1.sp_results.raceId == raceId) & (self.f1.sp_results.driverId == self.driverId)].values.flatten().tolist()
        sp_dict = dict()
        for index, result in enumerate(sprint_results_list):
            sp_dict.update({self.f1.results.sp_results.columns[index]:result})
        return sp_dict


    def results(self, year, circuit_id) -> dict:
        logger.info("%s, %s", year, circuit_id)
        raceId = self.race_id(year, circuit_id)
        results_list = self.f1.results[(self.f1.results.raceId == raceId) & (self.f1.results.driverId==self.driverId)].values.flatten().tolist()
        result_dict = dict()
        for index, result in enumerate(results_list):
            result_dict.update({self.f1.results.columns[index]:result})
        return result_dict

    def lap_info(self, year, circuit_id) -> pd.DataFrame:
        logger.info("%s, %s", year, circuit_id)
        raceId = self.race_id(year, circuit_id)
        lap_times = self.f1.laptimes[(self.f1.laptimes.raceId == raceId) & (self.f1.laptimes.driverId == self.driverId)]
        lap_times.time = lap_times.time.map(lambda x: datetime.timedelta(minutes=(datetime.datetime.strptime(x, "%M:%S.%f")).minute,
                                                                seconds=(datetime.datetime.strptime(x, "%M:%S.%f")).second,
                                                                microseconds=(datetime.datetime.strptime(x, "%M:%S.%f")).microsecond))
        lap_times["cumul_time"] = lap_times.time.cumsum(axis=None, skipna=True)
        logger.info("dtypes: %s", lap_times.dtypes)
        logger.info("lap times: %s", lap_times)
        return lap_times

    def pit_stops(self, year, circuit_id) -> pd.DataFrame:
        logger.info("%s, %s", year, circuit_id)
        raceId = self.race_id(year, circuit_id)
        pit_stops = self.f1.pitstops[(self.f1.pitstops.raceId == raceId) & (self.f1.pitstops.driverId == self.driverId)]
        return pit_stops

    def qualify_info(self, year, circuit_id) -> dict:
        logger.info("%s, %s", year, circuit_id)
        raceId = self.race_id(year, circuit_id)

        qualify = self.f1.qualifying[(self.f1.qualifying.raceId == raceId) & (self.f1.qualifying.driverId == self.driverId)].values.flatten().tolist()
        if len(qualify) == 0:
            qualify =  ["-"] * 9

        qualify_dict = dict()
        for index, qual in enumerate(qualify):
            key = self.f1.qualifying.columns[index]
            qualify_dict.update({key: qual})
        return qualify_dict

if __name__ == "__main__":
    charles_leclerc = Driver(844)
    print(charles_leclerc.basic_info())
    print(charles_leclerc.all_info())
    year = 2023
    circuitId = 80
    print(charles_leclerc.lap_info(year, circuitId))
    # print(charles_leclerc.circuit_ids(year))
    # print('results')
    # print(charles_leclerc.results(year, circuitId))
    # print(charles_leclerc.lap_info(year, circuitId))
    # print(charles_leclerc.pit_stops(year, circuitId))
    # print(charles_leclerc.qualify_info(year, circuitId))
