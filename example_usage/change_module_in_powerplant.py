"""This file contains the code for "Change the module in a power plant.." in the "Example Usage" section of the
documentation located at https://plantpredict-python.readthedocs.io."""

import plantpredict

# authenticate with client credentials and assign TOKEN variable in plantpredict/settings.py
plantpredict.OAuth2.token(client_id=plantpredict.settings.CLIENT_ID, client_secret=plantpredict.settings.CLIENT_SECRET)

# instantiate a prediction, specifying its ID and project ID (visible in the URL of that prediction in a web browser
# '.../projects/{project_id}/prediction/{id}/').
project_id = 7178   # CHANGE TO YOUR PROJECT ID
prediction_id = 45110   # CHANGE TO YOUR PREDICTION ID
prediction = plantpredict.Prediction(id=prediction_id, project_id=project_id)

# get the prediction in order to extract its powerplant ID
prediction.get()

# instantiate  powerplant and retrieve all of its attributes
power_plant = plantpredict.PowerPlant(prediction_id=prediction_id, project_id=project_id)
power_plant.get()

# get the ID of the module you want to replace the powerplant's current module with (visible in the URL
# of that module in a web browser '.../module/{id}/')
new_module_id = 1645

# in order to change the module in Block 1 --> Array 1 --> Inverter A --> DC Field 1,
# nullify the previous module's data structure, replace the module id, and update the power plant
power_plant.blocks[0]['arrays'][0]['inverters'][0]['dc_fields'][0]['module'] = None
power_plant.blocks[0]['arrays'][0]['inverters'][0]['dc_fields'][0]['module_id'] = new_module_id
power_plant.update()
