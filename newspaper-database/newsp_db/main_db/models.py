# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# for python 2 compatibility
from django.utils.encoding import python_2_unicode_compatible

## COMMENTS IS A TEXT FIELD

@python_2_unicode_compatible
class Owner(models.Model):
    CODES = (
        (0, 'Not Applicable'),
        (1, 'Investment'),
        (2, 'Private'),
        (3, 'Public'),
        (4, 'Independent')
    )
    owner_id = models.CharField(max_length=200, primary_key=True, unique=True)
    owner_name = models.CharField(max_length=200)
    owner_type = models.IntegerField(choices=CODES)

    def __str__(self):
        return self.owner_name

@python_2_unicode_compatible
class Newspaper(models.Model):
    newspaper_id = models.CharField(max_length=200, primary_key=True, unique=True)
    newspaper_name = models.CharField(max_length=400)
    city = models.CharField(max_length=200)
    black_ethnic = models.BooleanField()
    spa_full_member = models.BooleanField()
    owner_id = models.ForeignKey(Owner, db_column="owner_id",on_delete=models.PROTECT)

    def __str__(self):
        return self.newspaper_name

@python_2_unicode_compatible
class State(models.Model):
        STATES = (
            ('AK', 'Alaska'),
            ('AL','Alabama'),
            ('AR','Arkansas'),
            ('AZ','Arizona'),
            ('CA','California'),
            ('CO','Colorado'),
            ('CT','Connecticut'),
            ('DC','Washington, D.C.'),
            ('DE','Delaware'),
            ('FL','Florida'),
            ('GA','Georgia'),
            ('HI','Hawaii'),
            ('IA','Iowa'),
            ('ID','Idaho'),
            ('IL','Illinois'),
            ('IN','Indiana'),
            ('KS','Kansas'),
            ('KY','Kentucky'),
            ('LA','Louisiana'),
            ('MA','Massachussets'),
            ('MD','Maryland'),
            ('ME','Maine'),
            ('MI','Michigan'),
            ('MN','Minnesota'),
            ('MO','Missouri'),
            ('MS','Mississippi'),
            ('MT','Montana'),
            ('NC','North Carolina'),
            ('ND','North Dakota'),
            ('NE','Nevada'),
            ('NH','New Hampshire'),
            ('NJ','New Jersey'),
            ('NM','New Mexico'),
            ('NV','Nevada'),
            ('NY','New York'),
            ('OH','Ohio'),
            ('OK','Oklahoma'),
            ('OR','Oregon'),
            ('PA','Pennyslvania'),
            ('RI','Rhode Island'),
            ('SC','South Carolina'),
            ('SD','South Dakota'),
            ('TN','Tennessee'),
            ('TX','Texas'),
            ('UT','Utah'),
            ('VA','Virginia'),
            ('VT','Vermont'),
            ('WA','Washington'),
            ('WI','Wisconsin'),
            ('WV','West Virginia'),
            ('WY','Wyoming'),
        )
        state = models.CharField(max_length=2, choices=STATES, unique=True)

        def __str__(self):
            return self.state

@python_2_unicode_compatible
class County(models.Model):
    county_fips = models.CharField(max_length=4)
    county_name = models.CharField(max_length=400)
    state = models.ForeignKey(State, on_delete=models.PROTECT)

    def __str__(self):
        return self.county_name
