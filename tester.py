import sys
import json
from lambda_code.get_data import handler

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)
    with open('output.json', 'w') as result_file:
        (json.dump(handler(data, {}), result_file, indent=4))
