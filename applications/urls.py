# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.conf.urls import *

urlpatterns = patterns('applications.views',
    url(r'^$', 'index'),
    url(r'^new/', 'new_gadget' ),
    url(r'thanks$', TemplateView.as_view(template_name='app/thanks.html'), name="thanks"),
)
