import openai
import os
import json

fdir = os.path.dirname(__file__)
def getPath(fname):
    return os.path.join(fdir, fname)

configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
    config = json.load(configFile)

openai.api_key = config["openaiKey"]  # Replace with your API key

# Get the list of available models
models = openai.Model.list()

# Print out the available models
for model in models['data']:
    print(model['id'])

