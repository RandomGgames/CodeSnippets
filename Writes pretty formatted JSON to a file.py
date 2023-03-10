import json

#r is the json data being sent to file
with open('TEMP.json', 'w') as f: json.dump(r.json(), f, indent="\t")