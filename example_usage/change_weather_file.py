"""This file contains the code for "Change weather file." in the "Example Usage"
section of the documentation located at https://plantpredict-python.readthedocs.io."""

import plantpredict
from plantpredict.enumerations import WeatherDataProviderEnum, WeatherSourceTypeAPIEnum

# authenticate using API credentials
api = plantpredict.Api(
    username="insert username here",
    password="insert password here",
    client_id="insert client_id here",
    client_secret="insert client_secret here"
)

# Instantiate the prediction of interest specifying its ID and project ID (visible in the URL of that prediction
# in a web browser '.../projects/{project_id}/prediction/{id}/'). do the same for the project of interest.
project_id = 13161   # CHANGE TO YOUR PROJECT ID
prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
prediction = api.prediction(id=prediction_id, project_id=project_id)
project = api.project(id=project_id)

# retrieve the project and prediction
prediction.get()
project.get()

# in this particular case, let's say you are looking for the most recent Meteonorm weather file within a 5-mile
# radius of the project site. Search for all weather files within a 5 mile radius of the project's lat/long
# coordinates.
w = api.weather()
weathers = w.search(project.latitude, project.longitude, search_radius=5)

# filter the results by only Meteonorm weather files
weathers_meteo = [
    weather for weather in weathers if int(weather['data_provider']) == WeatherDataProviderEnum.METEONORM
]

# if there is a weather file that meets the criteria, used the most recently created weather file's ID.
# if no weather file meets the criteria, download a new Meteonorm weather file and use that ID
if weathers_meteo:
    created_dates = [w['created_date'] for w in weathers_meteo]
    created_dates.sort()
    idx = [w['created_date'] for w in weathers_meteo].index(created_dates[-1])
    weather_id = weathers_meteo[idx]['id']
else:
    weather = api.weather()
    response = weather.download(project.latitude, project.longitude, provider=WeatherSourceTypeAPIEnum.METEONORM)
    weather_id = weather.id

# instantiate weather using the weather ID, and retrieve all of its attributes
weather = api.weather(id=weather_id)
weather.get()

# ensure that the prediction start/end attributes match those of the weather file
prediction.start_date = weather.start_date
prediction.end_date = weather.end_date
prediction.start = weather.start_date
prediction.end = weather.end_date

# change the weather ID of the prediction, and update the prediction
prediction.weather_id = weather_id
prediction.update()
