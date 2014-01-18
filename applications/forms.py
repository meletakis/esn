# -*- coding: utf-8 -*-
import uuid

from django.forms import ModelForm
from applications.models import App, Data
from django.forms.models import inlineformset_factory
from django import forms



class AppForm (ModelForm):
	
	class Meta:
		model = App
		fields = ['Name','Author_email','Source_code_host', 'Description','responsibility', 'Domain']
		
		
class DataApplicationForm (ModelForm):
	class Meta:
		model = Data
		fields = ['Name','Data_Type', 'Domain']
		
#AppFormset = inlineformset_factory(Gadget, Data, fields=('data_name','input_type'), can_delete=False)		
		
		
