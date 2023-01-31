import streamlit as st
from datetime import date
from noaaplotter.utils import download_from_noaa
from datetime import datetime
from noaaplotter.noaaplotter import NOAAPlotter
import os


def date_picker_start(label):
    today = st.date_input(label, value=datetime(2022, 1, 1))
    return today


def date_picker_end(label):
    current_date = date.today()
    today = st.date_input(label, value=current_date)
    return today


def location_selector(my_dict):
    selected = st.selectbox('Choose an option', list(my_dict.keys()))
    return selected


# Create a dictionary
stations = {
'Anchorage':'GHCND:USW00026451',
'Kotzebue':'GHCND:USW00026616',
'Fairbanks': 'GHCND:USW00026411',
'Barrow':'GHCND:USW00027502',
'Bethel':'GHCND:USW00026615',
'Nome':'GHCND:USW00026617',
}

API_TOKEN = os.environ['NOAA_API_TOKEN']
# Widgets
start = datetime.strftime(date_picker_start("Start Date"), '%Y-%m-%d')
end = datetime.strftime(date_picker_end("End Date"), '%Y-%m-%d')
station_name = location_selector(stations)
product_selector = st.selectbox('Choose your plot type', ['daily', 'monthly'])

station_id = stations[station_name]
data_file = f'{station_name}.csv'

if st.button('Start Process'):
    download_from_noaa(data_file, '1980-01-01', end, ['TMIN', 'TMAX', 'PRCP', 'SNOW'], station_name, station_id, API_TOKEN)
    print('Successful')
    # plotting
    n = NOAAPlotter(data_file,
                    location=station_name,
                    climate_filtersize=7)
    if product_selector == 'daily':
        figure = n.plot_weather_series(start_date=start,
                              end_date=end,
                              show_snow_accumulation=False,
                              plot_extrema=True,
                              show_plot=False,
                              title=station_name,
                              return_plot=True)

    else:
        figure = n.plot_monthly_barchart(start_date=start,
                                end_date=end,
                                information='Temperature',
                                anomaly=True,
                                trailing_mean=12,
                                show_plot=False,
                                return_plot=True)
    st.pyplot(fig=figure, clear_figure=None)