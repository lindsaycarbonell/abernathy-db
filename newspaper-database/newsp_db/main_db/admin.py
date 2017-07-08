# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(Newspaper)
admin.site.register(Owner)
admin.site.register(State)
admin.site.register(County)
