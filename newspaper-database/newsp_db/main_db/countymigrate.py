import csv
from main_db.models import *

with open('static/main_db/county_census.csv') as f:
    print 'um hello'
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        # print row
        # print row[0]

        try:
            print 'trying...' + row[3]
            _, created = County.objects.get_or_create(
                county_fips = row[2],
                county_name = str(row[3]),
                state = State.objects.get(state=row[0]),
            )

        except State.DoesNotExist:
            print 'state does not exist'
            this_state = State(state=row[0])
            this_state.save()
            _, created = County.objects.get_or_create(
                county_fips = row[2],
                county_name = str(row[3]),
                state = State.objects.get(state=row[0]),
            )
