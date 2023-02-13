from datetime import datetime, date
import pandas as pd

import streamlit as st


def date_picker_start(label):
    today = st.date_input(label, value=datetime(2022, 1, 1))
    return today


def date_picker_end(label):
    current_date = date.today()
    today = st.date_input(label, value=current_date)
    return today


def location_selector(my_dict):
    selected = st.selectbox('Select Your Station', list(my_dict.keys()))
    return selected


def to_datestring(date):
    return datetime.strftime(date, '%Y-%m-%d')


def get_refperiod_from_widget(period_string):
    ref_start, ref_end = period_string.split('-')
    ref_start_date = datetime(int(ref_start), 1, 1)
    ref_end_date = datetime(int(ref_end), 12, 31)
    return ref_start_date, ref_end_date


def load_stations_from_NOAA(path):
    df = pd.read_fwf(path, header=None)[range(5)]
    cols = ['Station_ID', 'latitude', 'longitude','elevation', 'Station_name']
    df.columns = cols
    stations_dict = dict(df[['Station_name', 'Station_ID']].values)
    return stations_dict


def load_stations_from_pickle(link):
    df = pd.read_pickle(link)
    stations_dict = dict(df[['Station_name', 'Station_ID']].values)
    return stations_dict


def date_to_datetime(input_date):
    return datetime(input_date.year, input_date.month, input_date.day)