# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from applications import views


urlpatterns = patterns('applications',
    url(r'^$', view=login_required (views.index)),
    url(r'^new/', view=login_required (views.new_app2) ),
    url(r'^new2/', view=login_required (views.new_app2) ),
    url(r'^edit/', view=login_required (views.edit) ),
    url(r'^run/', view=login_required (views.run) ),
    url(r'^domain/new/', view=login_required (views.new_domain) ),
    url(r'thanks$', view=login_required (TemplateView.as_view(template_name='app/thanks.html') ), name="thanks"),
)
