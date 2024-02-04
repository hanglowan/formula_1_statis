from pathlib import Path
import os
import logging
import pandas as pd
import numpy as np

import fastf1

logging.basicConfig(format='%(asctime)s [%(name)s:%(lineno)d:%(funcName)s] [%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(Path(__file__).name)


class Session:
    def __init__(self, year, circuit):
        self.session = fastf1.get_session(year, circuit, "R")

        #todo temp
        # self.session.load(weather=False, messages=False)
    def load_session(self):
        self.session.load(weather=False, messages=False)

    def laps_participated(self, driver_id):
        laps = self.session.laps.pick_driver(driver_id).LapNumber.unique().astype('int64').tolist()
        return laps

    def get_circuit_info(self, type):
        if type == 'corners':
            return self.session.get_circuit_info().corners
        if type == 'marshal_lights':
            return self.session.get_circuit_info().marshal_lights
        if type == 'marshal_sectors':
            return self.session.get_circuit_info().marshal_sectors
        if type == 'rotation':
            return self.session.get_circuit_info().rotation

        raise Exception(f"Invalid Type Specified: {type}")

    def get_laps(self, driver_id):
        laps = self.session.laps.pick_driver(driver_id)
        return laps

    def get_tel(self, driver_id, lap_list:list):
        laps = self.session.laps.pick_driver(driver_id).pick_laps(lap_list).get_telemetry()
        return laps

    def get_event_info(self, col):
        return self.session.event[col]

    def get_total_laps(self):
        return int(max(session.laps.LapNumber.unique().tolist()))

    def get_driver_info(self, driver_id, col):
        return self.session.get_driver(driver_id)[col]

    def get_driver(self, driver_id):
        return self.session.get_driver(driver_id)

    def get_results(self, driver_id):
        results = self.session.results
        return results[results.Abbreviation == driver_id]
if __name__=='__main__':
    session = Session(2018, 2)
    # print(session.laps_participated("VET"))
    print(session.get_driver("VER"))
    # print(session.get_total_laps())
    print(session.get_tel("VET", [1]))



