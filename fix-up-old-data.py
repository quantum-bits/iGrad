#!/usr/bin/env python3

import json
from sys import argv

if len(argv) != 3:
    print("usage: {} <input file> <output file>".format(argv[0]))
    exit(1)

# Load 
dump = None
with open(argv[1], "r") as fp:
    records = json.load(fp)
    print("Read {} records from {}".format(len(records), argv[1]))

# Ouptut Statistics
model_types = {}
for record in records:
    model = record['model']
    if model not in model_types:
        model_types[model] = 0
    model_types[model] += 1

for k in sorted(model_types.keys()):
    print(k, model_types[k])

# Filter and munge
output = []
for record in records:
    model = record['model']
    if model.startswith('planner.') or model in ['auth.user']:
        output.append(record)
    # if model == 'contenttypes.contenttype':
    #     del record['fields']['name']
    #     print(record['fields']['app_label'], record['fields']['model'])
    #     output.append(record)

# Output result
with open(argv[2], "w") as fp:
    print("Writing {} records to {}".format(len(output), argv[2]))
    json.dump(output, fp, sort_keys=True, indent=4)
