from django.contrib import admin
from django.contrib.sites.models import RequestSite
from applications.models import App, Data,  IORegistry, Domain

admin.site.register(App)
admin.site.register(Data)
admin.site.register(IORegistry)
admin.site.register(Domain)
