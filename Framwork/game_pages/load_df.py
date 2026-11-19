# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import os
from pathlib import Path

import pandas as pd
import yaml


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


class DF_parser:
    def __get_df(self, df_name):
        """loads in given dataframe from config with given dataframe name"""
        # load in dataframe/pickle path
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        df_path = config[df_name]
        print(f"{df_name} df path: ", df_path)

        # check if file location of df pickles file exists
        if not os.path.exists(df_path):
            print("df {df_name} not correctly installed/couldnt find them. so cant make it work :(")
            raise FileNotFoundError("Required data frames is missing.")
        
        # load in pickle file to df object
        df = pd.read_pickle(df_path)
        
        # check if data is anonymized
        required_levels = {"date_time", "participant_num"}
        if not required_levels.issubset(df.index.names):
            TypeError(f"Dataframe {df_name} is missing the anonymized data")

        print(f"completed getting anonymized dataframe: {df_name}\n\n\n")
        return df

    def get_main(self):
        """returns main df based on given name"""
        return self.__get_df("main")

    def get_reading(self):
        """returns reading results df based on given name"""
        return self.__get_df("reading_comprehension")

    def get_maze(self):
        """returns maze results df based on given name"""
        return self.__get_df("maze")

    def get_digit_span(self):
        """returns digit span results df based on given name"""
        return self.__get_df("digit_span")

    def get_game_times(self):
        """returns game timestamps df based on given name"""
        return self.__get_df("game_times")
    
    def get_heart_rate(self):
        """returns heart rate df based on given name"""
        return self.__get_df("heart_rate")

    def squad_qa(self):
        """returns squad df using the config path for variable squad_df"""
        print(os.getcwd())
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        df_path = config["squad_df"]
        print(f"squad_df path: ", df_path)

        # check if file location of df pickles file exists
        if not os.path.exists(df_path):
            print("df {df_name} not correctly installed/couldnt find them. so cant make it work :(")
            raise FileNotFoundError("Required data frames is missing.")
        print("loaded SQUAD dataset")
        # load in pickle file to df object
        return pd.read_pickle(df_path)