import json
from pathlib import Path
from datetime import datetime, date

from faker import Faker

fake = Faker()

with Path('../data/secret/icu.json').open() as f:
    persons = json.load(f)
    persons = persons['data']

fields_to_fake = {
    'name': fake.name,
    'dob': fake.date_of_birth,
    'csn': fake.numerify,
}

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
            person['admission_age_years'] = date.today().year - replacement.year
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


with Path('../data/clean.json').open('w') as f:
    json.dump(persons, f, indent=4)
