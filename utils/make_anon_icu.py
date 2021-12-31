# run this script from the datascience desktop to deidentify sample data
# secrets is excluded from git etc
# expects a single json file from the icu/live API
# e.g
# curl -X 'GET' \
#   'http://uclvlddpragae08:5006/icu/live/T03/ui' \
#   -H 'accept: application/json'


import json
from pathlib import Path
from datetime import datetime, date
import argparse
from faker import Faker

parser = argparse.ArgumentParser(description="Anonymise data from ICU/Live API")
parser.add_argument('unit', type=str, help='Unit name: one of T03,T06')
args = parser.parse_args()

unit = args.unit.lower()
units = [i.lower() for i in ['T03', 'T06']]
assert unit in units 

fake = Faker()

with Path(f'data/secret/icu_{unit}.json').open() as f:
    persons = json.load(f)
    persons = persons['data']

fields_to_fake = {
    'name': fake.name,
    'dob': fake.date_of_birth,
    'csn': fake.numerify,
}

# Empty some beds 
beds_to_empty = ['SR02-02', 'BY02-19', 'BY03-24']
persons = [i for i in persons if i['bed_code'] not in beds_to_empty]

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
            person['admission_age_years'] = date.today().year - \
                replacement.year
            replacement = replacement.strftime("%Y-%m-%d")
            person[k] = replacement
        elif k == 'csn':
            replacement = fake.numerify("10########")
            person[k] = replacement
        elif k == 'mrn':
            replacement = fake.numerify("4#######")
            person[k] = replacement
        else:
            continue
        print(f"original: {v}   replacement: {replacement}")

# TODO Assert that change the content of the supplied JSON sampe but does NOT
# change the structure

with Path(f'data/icu_{unit}.json').open('w') as f:
    json.dump(persons, f, indent=4)
