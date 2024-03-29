#from datetime import datetime, date
import datetime
import pandas as pd
import streamlit as st
from noaaplotter.download_utils import download_from_noaa, download_era5_from_gee

def date_picker_start(label):
    today = st.date_input(label, value=datetime.datetime(2022, 1, 1))
    return today


def date_picker_end(label):
    current_date = datetime.date.today()
    today = st.date_input(label, value=current_date)
    return today


def location_selector(my_dict):
    selected = st.selectbox('Select Your Station', list(my_dict.keys()))
    return selected


def to_datestring(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d')


def get_refperiod_from_widget(period_string):
    ref_start, ref_end = period_string.split('-')
    ref_start_date = datetime.datetime(int(ref_start), 1, 1)
    ref_end_date = datetime.datetime(int(ref_end), 12, 31)
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
    return datetime.datetime(input_date.year, input_date.month, input_date.day)


@st.cache_data()  # Set allow_output_mutation to True for caching mutable objects like dictionaries
def load_data(dataset_selector, download_start, download_end, stations, API_TOKEN, station_name=None, coordinates_field=None):
    if dataset_selector == 'NOAA station':
        # get stations
        station_id = stations[station_name]
        data_file = f'NOAA_{station_id}.csv'
        n_jobs = 4
        try:
            download_from_noaa(data_file, download_start, download_end, ['TMIN', 'TMAX', 'PRCP', 'SNOW'], station_name,
                               station_id, API_TOKEN, n_jobs=n_jobs)
        except:
            n_jobs = 1
            download_from_noaa(data_file, download_start, download_end, ['TMIN', 'TMAX', 'PRCP', 'SNOW'], station_name,
                   station_id, API_TOKEN, n_jobs=n_jobs)
    elif dataset_selector == 'ERA5':
        """ERA5 data loading may take up to 5 minutes"""
        lat, lon = coordinates_field.replace(' ', '').split(',')
        data_file = f'ERA5_{lat}_{lon}.csv'
        station_name = None
        download_era5_from_gee(float(lat), float(lon), download_end, download_start, data_file)
    return data_file, station_name

def get_daily_dates():
    end_date = datetime.datetime.today()
    # Calculate one year before the current date
    one_year_before = end_date.replace(year=end_date.year-1) + datetime.timedelta(days=1)
    # Add one day to the calculated date
    start_date = one_year_before + datetime.timedelta(days=1)
    
    return start_date, end_date

def get_monthly_dates(years=20):
    today_datetime = datetime.datetime.today()
    # Calculate one year before the current date
    end_date = today_datetime.replace(day=1) + datetime.timedelta(days=-1)
    start_date = today_datetime.replace(day=1).replace(year=today_datetime.year-years)
    
    return start_date, end_date
