import streamlit as st
from noaaplotter.download_utils import download_from_noaa, download_era5_from_gee
import datetime
from noaaplotter.noaaplotter import NOAAPlotter
import os

from utils import to_datestring, get_refperiod_from_widget, load_stations_from_pickle, date_to_datetime

path = 'stations.z'
stations = load_stations_from_pickle(path)

API_TOKEN = os.environ['NOAA_API_TOKEN']
# containers
container_selectors = st.container()
columns_main = container_selectors.columns(2)
# widgets
dataset_selector = columns_main[0].selectbox('Choose your data source type', ['NOAA station', 'ERA5'])
refperiod_selector = columns_main[0].selectbox('Choose your climate reference period', ['1981-2010', '1991-2020'])
product_selector = columns_main[0].selectbox('Choose your plot type', ['daily', 'monthly'])
location_container = columns_main[1].container()
station_name = location_container.selectbox(
    'Select Your Station (NOAA Stations only)', list(stations.keys()), disabled=False)

coordinates_field = location_container.text_input('Please Insert Coordinates: LAT, LON (ERA5 only)')
infotype_selector = columns_main[1].selectbox(
    'Choose your Information Type (monthly only)', ['Temperature', 'Precipitation'], disabled=False)

# Date stuff
kwargs_date_picker = dict(min_value=datetime.datetime(1920, 1, 1))
# date container
container_date = st.container()
columns_date = container_date.columns(2)
start = columns_date[0].date_input(("Start Date"), value=datetime.datetime(2022, 1, 1), **kwargs_date_picker)
end = columns_date[1].date_input(("End Date"), value=datetime.datetime(2022, 12, 31), **kwargs_date_picker)
ref_start_date, ref_end_date = get_refperiod_from_widget(refperiod_selector)

# date conversions
start = date_to_datetime(start)
end = date_to_datetime(end)
download_start = to_datestring(min([start, ref_start_date]))
download_end = to_datestring(max([end, ref_end_date]))
# convert datetime to date_string
start_string = to_datestring(start)
end_string = to_datestring(end)

if st.button('Start Process'):
    # debug
    # download data
    if dataset_selector == 'NOAA station':
        # get stations
        station_id = stations[station_name]
        data_file = f'NOAA_{station_id}.csv'
        download_from_noaa(data_file, download_start, download_end, ['TMIN', 'TMAX', 'PRCP', 'SNOW'], station_name,
                           station_id, API_TOKEN)
    elif dataset_selector == 'ERA5':
        """ERA5 data loading may take up to 5 minutes"""
        lat, lon = coordinates_field.replace(' ', '').split(',')
        data_file = f'ERA5_{lat}_{lon}.csv'
        station_name = None
        download_era5_from_gee(float(lat), float(lon), download_end, download_start, data_file)

    # plotting
    n = NOAAPlotter(data_file, location=station_name, climate_filtersize=7,
                    climate_start=ref_start_date, climate_end=ref_end_date)
    if product_selector == 'daily':
        figure = n.plot_weather_series(start_date=start_string,
                                       end_date=end_string,
                                       show_snow_accumulation=False,
                                       plot_extrema=True,
                                       show_plot=False,
                                       title=station_name,
                                       return_plot=True)

    else:
        figure = n.plot_monthly_barchart(start_date=start_string,
                                         end_date=end_string,
                                         information=infotype_selector,
                                         anomaly=True,
                                         trailing_mean=12,
                                         show_plot=False,
                                         return_plot=True)
    st.pyplot(fig=figure, clear_figure=None)
