# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from applications import views

urlpatterns = patterns('applications',
    url(r'^$', view=login_required (views.index)),
    url(r'^new/', view=login_required (views.new_gadget) ),
    url(r'^developer/', view=login_required (views.developer)),
    url(r'thanks$', view=login_required (TemplateView.as_view(template_name='app/thanks.html') ), name="thanks"),
)
