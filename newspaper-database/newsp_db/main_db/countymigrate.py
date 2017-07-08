import csv
from main_db.models import *

with open('static/main_db/county_census.csv') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        print row
        print row[0]

    try:     
        _, created = County.objects.get_or_create(
            county_fips = row[2],
            county_name = str(row[3]),
            state = State.objects.get(state=row[0]),
        );

    except State.DoesNotExists:
        this_state = State(state=row[0])
        this_state.save()

        _, created = County.objects.get_or_create(
            county_fips = row[2],
            county_name = str(row[3]),
            state = State.objects.get(state=row[0]),
        );


# try:
#     pers_type = Person_Type.objects.get(pers_type='Appelant')
# except Person_Type.DoesNotExists:
#     person_type = Person_Type.objects.create(pers_type='Appellant')
# Person.objects.create(name='Adam', pers_type=pers_type)
