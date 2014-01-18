from django.contrib import admin
from django.contrib.sites.models import RequestSite
from responsibilities.models import Responsibility, Assignment

admin.site.register(Responsibility)
admin.site.register(Assignment)

