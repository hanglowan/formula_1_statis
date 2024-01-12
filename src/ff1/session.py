from pathlib import Path
import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(format='%(asctime)s [%(name)s:%(lineno)d:%(funcName)s] [%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(Path(__file__).name)


class Session:
    def __init__(self, year, circuit):
        # get cache data
        cache_dir = Path(Path(__file__).parent.parent.parent, 'f1_cache')
        logger.info("Cache Dir: %s", cache_dir)

        dirs = [x[0] for x in os.walk(f"{cache_dir}/{year}/")]
        logger.info("Year Dirs: %s", dirs)

        if type(circuit) is int or circuit.isnumeric():
            session_dir = dirs[int(circuit)]
        else:
            circuit = circuit.replace(" ", "_")
            if any(circuit in dir for dir in dirs):
                session_dir = [dir for dir in dirs if circuit in dir][0]
            else:
                logger.error(f"no dir found for {year}, {circuit}")
                raise KeyError
        logger.info("Session Dir: %s", session_dir)
        self.name = session_dir.replace("/", " ")

        try:
            self.car_data = pd.read_csv(Path(session_dir, 'car_data.csv'),
                                        parse_dates=[2],
                                        date_format='%Y-%m-%d %H:%M:%S.%f'
                                        )
            self.car_data.Time = pd.to_timedelta(self.car_data.Time)
            self.car_data.SessionTime = pd.to_timedelta(self.car_data.SessionTime)
        except FileNotFoundError:
            self.car_data = None
            logger.warning("No car_data")

        try:
            self.pos_data = pd.read_csv(Path(session_dir, 'pos_data.csv'),
                                        parse_dates=[2],
                                        date_format='%Y-%m-%d %H:%M:%S.%f'
                                        )
            self.pos_data.Time = pd.to_timedelta(self.pos_data.Time)
            self.pos_data.SessionTime = pd.to_timedelta(self.pos_data.SessionTime)
        except FileNotFoundError:
            self.pos_data = None
            logger.warning("No pos_data")

        try:
            self.tel_data = pd.read_csv(Path(session_dir, 'tel_data.csv'),
                                        parse_dates=[2],
                                        date_format='%Y-%m-%d %H:%M:%S.%f'
                                        )
            self.tel_data.Time = pd.to_timedelta(self.tel_data.Time)
            self.tel_data.SessionTime = pd.to_timedelta(self.tel_data.SessionTime)

        except FileNotFoundError:
            self.tel_data = None
            logger.warning("No tel_data")

        self.event_data = pd.read_csv(Path(session_dir, 'event_data.csv'),
                                      parse_dates=[8, 11, 14, 17, 20],
                                      date_format='%Y-%m-%d %H:%M:%S%z'
                                      )

        for i in range(1, 6):
            self.event_data[f'Session{i}DateUtc'] = pd.to_datetime(self.event_data[f'Session{i}DateUtc'])

        self.event_data['EventDate'] = pd.to_datetime(self.event_data['EventDate'])

        self.lap_data_general = pd.read_csv(Path(session_dir, 'lap_data_general.csv'),
                                            parse_dates=[24],
                                            date_format='%Y-%m-%d %H:%M:%S.%f'
                                            )
        to_timedelta = ['Time', 'LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time',
                        'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime', 'LapStartTime']

        for col in to_timedelta:
            self.lap_data_general[col] = pd.to_timedelta(self.lap_data_general[col])

        self.lap_data_general['IsPersonalBest'] = self.lap_data_general['IsPersonalBest'].astype('bool')


        self.result_data = pd.read_csv(Path(session_dir, 'result_data.csv'))
        self.result_data['Time'] = pd.to_timedelta(self.result_data['Time'])

        self.session_status = pd.read_csv(Path(session_dir, 'session_status.csv'))
        self.track_status = pd.read_csv(Path(session_dir, 'track_status.csv'))
        try:
            self.circuit_info = pd.read_csv(Path(session_dir, 'circuit_info.csv'))
        except FileNotFoundError:
            self.circuit_info = None

        self.driver_data = pd.read_csv(Path(session_dir, 'driver_data.csv'))


    def laps_participated(self, driver_id):
        laps = self.lap_data_general
        driver_laps = laps[laps.Driver == driver_id]
        laps = list(driver_laps.LapNumber.astype('int64'))
        return laps

    def get_circuit_info(self, type):
        circuit = self.circuit_info
        return circuit[circuit.Type==type]

    def get_laps(self, driver_id):
        laps = self.lap_data_general
        return laps[laps.Driver==driver_id]

    def get_tel(self, driver_id, lap_list:list):
        laps = self.tel_data
        laps = laps[(laps.Driver==driver_id) & (laps.Lap.isin(lap_list))]

        return laps

    def get_event_info(self, col):
        return self.event_data[col].iloc[0]

    def get_total_laps(self):
        return int(max(list(self.lap_data_general.LapNumber.unique())))

    def get_driver_info(self, driver_id, col):
        return self.driver_data[self.driver_data.Abbreviation==driver_id][col].iloc[0]

    def get_driver(self, driver_id):
        driver = self.driver_data[self.driver_data.Abbreviation == driver_id].to_dict('index')

        return driver[list(driver.keys())[0]]

if __name__=='__main__':
    session = Session(2018, 2)
    # print(session.get_total_laps())
    # print(session.get_driver("VET"))
    print(session.get_tel("VET", [1]))



