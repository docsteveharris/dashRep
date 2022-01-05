# run this script from the datascience desktop to deidentify sample data
# secrets is excluded from git etc
# expects a single json file from the emap/census API
# e.g
# curl -X 'GET' \
  # 'http://uclvlddpragae08:5006/emap/census/T03/' \
  # -H 'accept: application/json'


import json
from pathlib import Path
from datetime import datetime, date
import random
import argparse

from faker import Faker

units = ['T03', 'T06', 'WMS']
parser = argparse.ArgumentParser(description="Anonymise data from emap/census API")
parser.add_argument('unit', type=str, help=f"Unit name: one of {', '.join(units)}")
args = parser.parse_args()

unit = args.unit.lower()
units = [i.lower() for i in units]
assert unit in units 

fake = Faker()

with Path(f'data/secret/census_{unit}.json').open() as f:
    persons = json.load(f)
    persons = persons['data']

# Make your own ethnicity faker
ethnicities = [p['ethnicity'] for p in persons]



for person in persons:
    for k, v in person.items():
        if k == 'name':
            if person['sex'] == "F":
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name_male()
            replacement = f"{first_name} {fake.last_name()}"
            person[k] = replacement
        elif k == 'dob':
            replacement = fake.date_of_birth()
            replacement = replacement.strftime("%Y-%m-%d")
            person[k] = replacement
        elif k == 'csn':
            replacement = fake.numerify("10########")
            person[k] = replacement
        elif k == 'mrn':
            replacement = fake.numerify("4#######")
            person[k] = replacement
        elif k == 'postcode':
            replacement = fake.postcode()
            person[k] = replacement
        elif k == 'ethnicity':
            replacement = random.sample(ethnicities, 1)
            person[k] = replacement
        else:
            print(f'WARNING: No action for {k}')
            continue
        print(f"original: {v}   replacement: {replacement}")

# TODO Assert that change the content of the supplied JSON sampe but does NOT
# change the structure

with Path(f'data/census_{unit}.json').open('w') as f:
    json.dump(persons, f, indent=4)
