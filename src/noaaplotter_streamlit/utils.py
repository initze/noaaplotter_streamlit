import datetime

import pandas as pd
import streamlit as st
from noaaplotter.utils.download_utils import download_era5_from_gee, download_from_noaa


def date_picker_start(label):
    """
    A function to display a date picker in a Streamlit app.

    Args:
        label (str): The label for the date picker.

    Returns:
        datetime.date: The selected date.
    """
    today = st.date_input(label, value=datetime.datetime(2022, 1, 1))
    return today


def date_picker_end(label):
    """
    A function to display a date picker in a Streamlit app for selecting the end date.

    Args:
        label (str): The label for the date picker.

    Returns:
        datetime.date: The selected end date.
    """
    current_date = datetime.date.today()
    today = st.date_input(label, value=current_date)
    return today


def location_selector(my_dict):
    """
    A function to display a dropdown selector in a Streamlit app.

    Args:
        my_dict (dict): A dictionary containing the options for the selector.

    Returns:
        str: The selected option.
    """
    selected = st.selectbox("Select Your Station", list(my_dict.keys()))
    return selected


def to_datestring(date):
    """
    Converts a datetime.date object to a string in the format "YYYY-MM-DD".

    Args:
        date (datetime.date): The date object to convert.

    Returns:
        str: The date string.
    """
    return datetime.datetime.strftime(date, "%Y-%m-%d")


def get_refperiod_from_widget(period_string):
    """
    Parses a reference period string and returns the start and end dates as datetime objects.

    Args:
        period_string (str): A string in the format "YYYY-YYYY" representing the reference period.

    Returns:
        tuple: A tuple containing two datetime.datetime objects, representing the start and end dates of the reference period.
    """
    ref_start, ref_end = period_string.split("-")
    ref_start_date = datetime.datetime(int(ref_start), 1, 1)
    ref_end_date = datetime.datetime(int(ref_end), 12, 31)
    return ref_start_date, ref_end_date


def load_stations_from_NOAA(path):
    """
    Loads station data from a NOAA file and returns a dictionary mapping station names to station IDs.

    Args:
        path (str): The path to the NOAA file.

    Returns:
        dict: A dictionary mapping station names to station IDs.
    """
    df = pd.read_fwf(path, header=None)[range(5)]
    cols = ["Station_ID", "latitude", "longitude", "elevation", "Station_name"]
    df.columns = cols
    stations_dict = dict(df[["Station_name", "Station_ID"]].values)
    return stations_dict


def load_stations_from_pickle(link):
    """
    Loads station data from a pickle file and returns a dictionary mapping station names to station IDs.

    Args:
        link (str): The link to the pickle file.

    Returns:
        dict: A dictionary mapping station names to station IDs.
    """
    df = pd.read_pickle(link)
    stations_dict = dict(df[["Station_name", "Station_ID"]].values)
    return stations_dict


def date_to_datetime(input_date):
    """
    Converts a datetime.date object to a datetime.datetime object.

    Args:
        input_date (datetime.date): The date to be converted.

    Returns:
        datetime.datetime: The converted datetime object.
    """
    return datetime.datetime(input_date.year, input_date.month, input_date.day)


@st.cache_data()  # Set allow_output_mutation to True for caching mutable objects like dictionaries
def load_data(
    dataset_selector,
    download_start,
    download_end,
    stations,
    API_TOKEN,
    station_name=None,
    coordinates_field=None,
):
    """
    Loads data from a selected dataset source.

    Args:
        dataset_selector (str): The dataset source, either "NOAA station" or "ERA5".
        download_start (datetime.date): The start date for data downloading.
        download_end (datetime.date): The end date for data downloading.
        stations (dict): A dictionary mapping station names to station IDs.
        API_TOKEN (str): The API token for accessing NOAA data.
        station_name (str, optional): The name of the station to download data for. Required if dataset_selector is "NOAA station".
        coordinates_field (str, optional): The latitude and longitude coordinates in the format "latitude,longitude". Required if dataset_selector is "ERA5".

    Returns:
        tuple: A tuple containing the path to the downloaded data file and the station name (None if not applicable).
    """
    if dataset_selector == "NOAA station":
        # get stations
        station_id = stations[station_name]
        data_file = f"NOAA_{station_id}.csv"
        n_jobs = 3
        try:
            download_from_noaa(
                data_file,
                download_start,
                download_end,
                ["TMIN", "TMAX", "PRCP", "SNOW"],
                station_name,
                station_id,
                API_TOKEN,
                n_jobs=n_jobs,
            )
        except:
            n_jobs = 1
            download_from_noaa(
                data_file,
                download_start,
                download_end,
                ["TMIN", "TMAX", "PRCP", "SNOW"],
                station_name,
                station_id,
                API_TOKEN,
            )
    elif dataset_selector == "ERA5":
        """ERA5 data loading may take up to 5 minutes"""
        lat, lon = coordinates_field.replace(" ", "").split(",")
        data_file = f"ERA5_{lat}_{lon}.csv"
        station_name = None
        download_era5_from_gee(
            float(lat), float(lon), download_end, download_start, data_file
        )
    return data_file, station_name


def get_daily_dates():
    """
    Returns the start and end dates for a daily data period.

    Returns:
        tuple: A tuple containing the start and end dates.
    """
    end_date = datetime.datetime.today()
    # Calculate one year before the current date
    one_year_before = end_date.replace(year=end_date.year - 1) + datetime.timedelta(
        days=1
    )
    # Add one day to the calculated date
    start_date = one_year_before + datetime.timedelta(days=1)

    return start_date, end_date


def get_monthly_dates(years=20):
    """
    Returns the start and end dates for a monthly data period.

    Args:
        years (int, optional): The number of years to go back from the current date. Defaults to 20.

    Returns:
        tuple: A tuple containing the start and end dates.
    """
    today_datetime = datetime.datetime.today()
    # Calculate one year before the current date
    end_date = today_datetime.replace(day=1) + datetime.timedelta(days=-1)
    start_date = today_datetime.replace(day=1).replace(year=today_datetime.year - years)

    return start_date, end_date
