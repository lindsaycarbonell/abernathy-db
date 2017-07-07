# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# for python 2 compatibility
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Owner(models.Model):
    owner_id = models.CharField(max_length=200, primary_key=True, unique=True)
    owner_name = models.CharField(max_length=200)
    owner_type = models.CharField(max_length=200)
    owner_type_code = models.CharField(max_length=200)

    def __str__(self):
        return self.owner_name

    def __unicode__(self):
        return self.owner_name

@python_2_unicode_compatible
class Newspaper(models.Model):
    newspaper_id = models.CharField(max_length=200, primary_key=True, unique=True)
    newspaper_name = models.CharField(max_length=400)
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=200)
    county = models.CharField(max_length=200)
    black_ethnic = models.BooleanField()
    spa_full_member = models.BooleanField()
    owner_id = models.ForeignKey(Owner, db_column="owner_id",on_delete=models.PROTECT)

    def __str__(self):
        return self.newspaper_name
