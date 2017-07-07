# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Newspaper
from .models import Owner

admin.site.register(Newspaper)
admin.site.register(Owner)
