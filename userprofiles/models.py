# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from roleapp.models import Role
from registration.models import RegistrationProfile
from django.utils.translation import ugettext_lazy as _
from cicu.widgets import CicuUploaderInput
from esn.settings import MEDIA_ROOT
from django import forms

class uploadedImage (models.Model):
    image = models.ImageField(verbose_name="", null=True, blank=True, upload_to=MEDIA_ROOT, max_length=300)

class freeCrop(forms.ModelForm):
    class Meta:
        model = uploadedImage
        cicuOptions = {
            'ratioWidth': '', #if image need to have fix-width ratio
            'ratioHeight':'', #if image need to have fix-height ratio
            'sizeWarning': 'False', #if True the crop selection have to respect minimal ratio size defined above.
        }
        widgets = {
            'image': CicuUploaderInput(options=cicuOptions)
        }

class profileCrop(forms.ModelForm):
    class Meta:
        model = uploadedImage
        cicuOptions = {
            'ratioWidth': '200', #if image need to have fix-width ratio
            'ratioHeight':'200', #if image need to have fix-height ratio
            'sizeWarning': 'False', #if True the crop selection have to respect minimal ratio size defined above.
        }
        widgets = {
            'image': CicuUploaderInput(options=cicuOptions)
        }

class Activities(models.Model):
	activity = models.CharField(max_length=200L)

	def __str__(self):
		return str(self.activity)
	
	def __unicode__(self):
		return unicode(self.activity)

	class Meta:
		verbose_name = _("Δραστηριότητες")
        	verbose_name_plural= _("Δραστηριότητες")

class UserProfile(models.Model):
	
	user = models.ForeignKey(User, unique=True)
	role = models.ForeignKey(Role)
	
	#ADDED FOR WALL POSTS
	#image = models.ImageField(upload_to='user_images', verbose_name=_('Avatar'), blank=True, null=True)
	#friends = models.ManyToManyField(User, verbose_name=_('Friends'), blank=True, null=True, related_name='friends')
	#last_visit = models.DateTimeField(blank=True, auto_now=True, verbose_name=_('Last visit'))

	aboutMe = models.TextField(verbose_name="Περιγραφή",blank=True)
	displayName = models.CharField(verbose_name="Εμφανιζόμενο Όνομα",max_length=45L, blank=True)
	email = models.CharField(verbose_name="E-mail",max_length=45L, blank=True)
	location = models.CharField(verbose_name="Περιοχή",max_length=45L, blank=True)
	name = models.CharField(verbose_name="Ονοματεπώνυμο",max_length=45L, blank=True)
	status = models.CharField(verbose_name="Οικογενειακή Κατάσταση",max_length=45L, blank=True)
	thumbnailURL = models.CharField(verbose_name="Εικόνα",max_length=200L, db_column='thumbnailURL', blank=True, default='/static/main/img/user.png')
	activities = models.ManyToManyField(Activities)
	studies = models.TextField(verbose_name="Σπουδές",blank=True)
	birthday = models.DateField(verbose_name="Ημερομηνία Γέννησης",null=True, blank=True)
	favouriteFood = models.TextField(verbose_name="Αγαπημένο φαγητό",blank=True)
	favouriteSport = models.TextField(verbose_name="Αγαπημένο άθλημα",blank=True)
	gender = models.CharField(verbose_name="Φύλο",max_length=45L, blank=True)
	interests = models.CharField(verbose_name="Ενδιαφέροντα",max_length=45L, blank=True)
	#company = models.CharField(max_length=50, blank=True)
	
	

	def __str__(self):
		return str(self.user)
	def __unicode__(self):
		return unicode(self.user)

	class Meta:
		verbose_name = _('User Profile')
		verbose_name_plural = _('User Profiles')
	
	

		
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])	
