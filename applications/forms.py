# -*- coding: utf-8 -*-
import uuid

from django.forms import ModelForm
from applications.models import App, Data
from django.forms.models import inlineformset_factory
from django import forms



class AppForm (ModelForm):
	
	class Meta:
		model = App
		fields = ['name','description','domain','source_code_host','responsibility']
		
		
class DataApplicationForm (ModelForm):
	class Meta:
		model = Data
		fields = ['name','data_type', 'domain']
		
#AppFormset = inlineformset_factory(Gadget, Data, fields=('data_name','input_type'), can_delete=False)		
		
		
