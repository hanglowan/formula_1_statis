import pandas as pd
from datetime import datetime
import datetime as dt
import os
import logging
from pathlib import Path

logger = logging.getLogger(Path(__file__).name)

class Drivers:
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        relative_path = "../../f1_data/drivers.csv"
        full_path = os.path.join(absolute_path, relative_path)

        self.drivers = pd.read_csv(full_path)
        self.drivers.dob = pd.to_datetime(self.drivers.dob)

        self.drivers = self.drivers.rename(columns={'forename': 'first',
                                                    'surname': 'last'})

        # for col in ['first', 'last', 'nationality']:
        #     self.drivers[col] = self.drivers[col].map(lambda x: x.lower())
        self.drivers.set_index('driverId')
        # self.drivers.sort_values(by='dob', axis=0, ascending=True)
        self.drivers['age'] = self.drivers.dob.map(lambda x: dt.date.today().year-x.year)
        self.drivers = self.drivers.sort_values('age', ascending=True)
        cols = list(self.drivers.columns.values)[:-1]
        cols.insert(6, 'age')
        self.drivers = self.drivers[cols]
        self.drivers['dob'] = self.drivers.dob.dt.strftime("%B %d, %Y")

    def get_driver_id(self, code):
        return self.drivers[self.drivers.code==code].driverId.iloc[0]

    def get_info(self, driverId) -> list:
        if driverId not in self.drivers.driverId.tolist():
            return ["-"]*len(self.drivers.columns)
        return self.drivers[self.drivers.driverId==driverId].values.flatten().tolist()
        
    def get_columns(self):
        return self.drivers.columns

    def get_driver(self, id:int) -> str:
        return self.drivers[self.drivers.driverId==id]['first'].iloc[0] + " " +\
            self.drivers[self.drivers.driverId==id]['last'].iloc[0]
    
    def get_col_values(self, attribute:str):
        if attribute not in self.drivers.columns:
            logger.error("%s not found in drivers.", attribute)
            return None

        return self.drivers[attribute]

    def get_rows(self, attribute:str, id_list:list):
        if attribute not in self.drivers.columns:
            logger.error("%s not found in drivers.", attribute)
            return None
        if attribute in ['driverId', 'number']:
            try:
                for i in range(len(id_list)):
                    id_list[i] = int(id_list[i])
            except:
                logger.error("%s cannot be converted to int in %s", id, attribute)
                return None
        if attribute == 'dob':
            try:
                for i in range(len(id_list)):
                    id_list[i] = datetime.strptime(id_list[i], '%Y-%m-%d')

            except:
                logger.error("%s cannot be converted to int in %s", id, attribute)
                return None

        return self.drivers[self.drivers[attribute].isin(id_list)]

    def get_drivers(self):
        return self.drivers



# if __name__ == '__main__':

    # x = [print(df[col]) for col in drivers.get_columns()]
    # print(drivers.get_rows('last', 'leclerc'))
