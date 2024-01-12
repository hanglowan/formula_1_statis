import pandas as pd
import os

class Ctors():
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        relative_path = "../../f1_data/constructors.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.ctors = pd.read_csv(full_path)

        relative_path = "../../f1_data/constructor_results.csv"
        full_path = os.path.join(absolute_path, relative_path)
        self.ctor_results = pd.read_csv(full_path)


    def get_constructor_name(self, ctorId) -> str:
        return self.ctors[self.ctors.constructorId==ctorId]['name'].iloc[0]

    def get_constructor_nationality(self, ctorId):
        return self.ctors[self.ctors.constructorId == ctorId]['nationality'].iloc[0]
