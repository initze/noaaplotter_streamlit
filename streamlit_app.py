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
    selected = st.selectbox('Select Your Station', list(my_dict.keys()))
    return selected


def to_datestring(date):
    return datetime.strftime(date, '%Y-%m-%d')

# Create a dictionary
stations = {
'Anchorage':'USW00026451',
'Kotzebue':'USW00026616',
'Fairbanks': 'USW00026411',
'Barrow':'USW00027502',
'Bethel':'USW00026615',
'Nome':'USW00026617',
}

API_TOKEN = os.environ['NOAA_API_TOKEN']
# Widgets

container_selectors = st.container()
dataset_selector = container_selectors.selectbox('Choose your data source type', ['NOAA station', 'ERA5'])
station_name = selected = st.selectbox('Select Your Station', list(stations.keys()))
product_selector = container_selectors.selectbox('Choose your plot type', ['daily', 'monthly'])
infotype_selector = container_selectors.selectbox('Choose your Information Type', ['Temperature', 'Precipitation'])
refperiod_selector = container_selectors.selectbox('Choose your climate reference period', ['1981-2010', '1991-2020'])

# Plot period
kwargs_date_picker = dict(min_value=datetime(1920, 1, 1))
start = st.date_input(("Start Date"), value=datetime(2022, 1, 1), **kwargs_date_picker)
end = st.date_input(("End Date"), value=datetime(2022, 12, 31), **kwargs_date_picker)



# convert datetime to date_string
start_string = to_datestring(start)
end_string = to_datestring(end)
today = to_datestring(datetime.today())

station_id = stations[station_name]
data_file = f'{station_name}.csv'

if st.button('Start Process'):
    download_from_noaa(data_file, '1980-01-01', today, ['TMIN', 'TMAX', 'PRCP', 'SNOW'], station_name, station_id, API_TOKEN)
    print('Successful')
    # plotting
    n = NOAAPlotter(data_file,
                    location=station_name,
                    climate_filtersize=7)
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