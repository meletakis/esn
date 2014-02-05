# -*- coding: utf-8 -*-
import uuid

from django.forms import ModelForm
from applications.models import App, Data, Domain
from django.forms.models import inlineformset_factory
from django import forms



class AppForm (ModelForm):
	
	class Meta:
		model = App
		fields = ['name','description','domain','source_code_host','responsibility']
		
		
class DataApplicationForm (ModelForm):
	class Meta:
		model = Data
		fields = ['data_type','name', 'domain','description']
		exclude = ('app',)
		
#AppFormset = inlineformset_factory(Gadget, Data, fields=('data_name','input_type'), can_delete=False)		
		
class DomainForm (ModelForm):
	class Meta:
		model = Domain
		fields = ['Name', 'Description']


class AppForm2 (ModelForm):
	
	class Meta:
		model = App
		fields = ['name','description','domain','source_code_host','responsibility']
		
		
class DataApplicationForm2 (ModelForm):
	class Meta:
		model = Data
		fields = ['data_type','name', 'domain','description','slug']
		exclude = ('app',)
