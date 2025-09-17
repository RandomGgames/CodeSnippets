import json

#                                           {} is the JSON data being printed to file
with open('TEMP.json', 'w') as f:
    json.dump({}, f, indent="\t")
