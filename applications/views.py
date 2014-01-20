from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse, HttpResponseRedirect
from applications.forms import AppForm, DataApplicationForm
from applications.models import App, Data, IORegistry
from userprofiles.models import UserProfile
from django.contrib.contenttypes.models import ContentType
from responsibilities.models import Responsibility, Assignment
from roleapp.models import Role



def index(request):
	
    user = UserProfile.objects.get( user_id = request.user.id )
    role_ct = ContentType.objects.get(app_label="roleapp", model="role")
    user_ct = ContentType.objects.get(app_label="auth", model="user")
    #user_role = Role.objects.get (id = user.role_id)
    #print user_role
    #print role_ct
    #print user.role_id
    try:
        user_assigments = Assignment.objects.get(content_type_id = role_ct, object_id = user.role_id )
        apps = App.objects.filter(responsibility_id = user_assigments.Responsibility_id )
    except Exception, e:
        apps = []
    else:
        pass
    finally:
        pass

    try:
        print "pray"
        user_assigments = Assignment.objects.get(content_type_id = user_ct, object_id = request.user.id )
        print user_assigments
        apps += App.objects.filter(responsibility_id = user_assigments.Responsibility_id )
    except Exception, e:
        pass
    else:
        pass
    finally:
        pass
    print apps
    return render(request, 'app.html', {'apps' : apps })


def new_gadget(request):

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    App_Data_FormSet = formset_factory(DataApplicationForm, max_num=10, formset=RequiredFormSet)

	#check for developer Role
    if str(request.user.profile.role) != "Developer":
		return HttpResponseRedirect('/')
	

    if request.method == 'POST': # If the form has been submitted...
        app_form = AppForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        app_data_formset = App_Data_FormSet(request.POST, request.FILES)
        print "IN POST"
        
        if app_form.is_valid() and app_data_formset.is_valid():
            app_name = app_form.cleaned_data['Name']
            email = app_form.cleaned_data['Author_email']
            source = app_form.cleaned_data['Source_code_host']
            resp = app_form.cleaned_data['responsibility']
            desc = app_form.cleaned_data['Description']
            domain = app_form.cleaned_data['Domain']
            app_obj = App(Name=app_name, Author_email=email, Source_code_host=source, responsibility = resp, Description = desc, Domain = domain)
            app_obj.save()
            app_obj.Source_code_host = source+'?app_id='+str(app_obj.id)
            app_obj.save()
            
            for form in app_data_formset.forms:
                data_name = form.cleaned_data['Name']
                dat_type = form.cleaned_data['Data_Type']
                domain = form.cleaned_data['Domain']
                data_obj = Data ( App = app_obj, Name = data_name, Data_Type = dat_type,Domain = domain )
                data_obj.save()

                if ( dat_type == "Output"):
                    ioregistry_obj = IORegistry ( App = app_obj , Data = data_obj, Type = dat_type)
                    print ioregistry_obj
                    ioregistry_obj.save()
                else:
                    ioregistry_obj = IORegistry ( App = app_obj , Data = data_obj, Type = "Input")
                    print ioregistry_obj
                    ioregistry_obj.save()


            return HttpResponseRedirect('/apps/thanks') # Redirect to a 'success' page
        else:
            print "FORM VALIDATION ERROR"
            #print app_form.cleaned_data
            #for form in app_data_formset.forms:
                #print form.cleaned_data
    else:
        app_form = AppForm()
        app_data_formset = App_Data_FormSet()
    
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'app_form': app_form,
         'app_data_formset': app_data_formset,
        }
    c.update(csrf(request))
    
    return render_to_response('app/index.html', c)


def developer(request):
	if request.user.profile.role == "Developer":
		return HttpResponseRedirect('/')
		

