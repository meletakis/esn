from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse, HttpResponseRedirect
from applications.forms import AppForm, DataApplicationForm, DomainForm, DataApplicationForm2, AppForm2
from applications.models import App, Data, IORegistry, Domain, IORegistry
from userprofiles.models import UserProfile
from django.contrib.contenttypes.models import ContentType
from responsibilities.models import Responsibility, Assignment
from roleapp.models import Role
from django.contrib.auth.models import User
from django.utils import simplejson
from userprofiles.models import UserProfile
from django.db.models import Q
from notifications import notify



def index(request):
    
    if str(request.user.profile.role) == "Developer":
        return render(request, 'app/developer.html',)
    else: 
        user = UserProfile.objects.get( user_id = request.user.id )
        role_ct = ContentType.objects.get(app_label="roleapp", model="role")
        user_ct = ContentType.objects.get(app_label="auth", model="user")

        try:
            user_assigments = Assignment.objects.get(content_type_id = role_ct, object_id = user.role_id )
            apps = App.objects.filter(responsibility_id = user_assigments.Responsibility_id )
        except Exception, e:
            apps = []
        else:
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

        return render(request, 'app.html', {'apps' : apps })


def new_app(request):

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    App_Data_FormSet = formset_factory(DataApplicationForm, max_num=10, formset=RequiredFormSet)
    app_data = IORegistry.objects.all().filter(data_type = "Output").values_list( 'data')
    print app_data
    #profile_data = UserProfile.objects.all().values_list('aboutMe', 'displayName', 'email')
    profile_data = UserProfile._meta.get_all_field_names()
    #print profile_data
    #print type (profile_data)

    #check for developer Role
    if str(request.user.profile.role) != "Developer":
        return HttpResponseRedirect('/')
    

    if request.method == 'POST': # If the form has been submitted...
        app_form = AppForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        app_data_formset = App_Data_FormSet(request.POST, request.FILES)
        print "IN POST"
        
        if app_form.is_valid() and app_data_formset.is_valid():
            app_name = app_form.cleaned_data['name']
            source = app_form.cleaned_data['source_code_host']
            resp = app_form.cleaned_data['responsibility']
            desc = app_form.cleaned_data['description']
            domain = app_form.cleaned_data['domain']
            app_obj = App(name=app_name, author=request.user, source_code_host=source, responsibility = resp, description = desc, domain = domain)
            app_obj.save()
            app_obj.Source_code_host = source+'?app_id='+str(app_obj.id)
            app_obj.save()
            
            for form in app_data_formset.forms:
                data_name = form.cleaned_data['name']
                dat_type = form.cleaned_data['data_type']
                domain = form.cleaned_data['domain']
                description = form.cleaned_data['description']
                data_obj = Data ( app = app_obj, name = data_name, data_type = dat_type, domain = domain , description = description)
                data_obj.save()

                if ( dat_type == "Output"):
                    ioregistry_obj = IORegistry ( app = app_obj , data = data_obj, data_type = dat_type)
                    print ioregistry_obj
                    ioregistry_obj.save()
                else:
                    ioregistry_obj = IORegistry ( app = app_obj , data = data_obj, data_type = "Input")
                    print ioregistry_obj
                    ioregistry_obj.save()


            return HttpResponseRedirect('/apps/') # Redirect to a 'success' page
        else:
            print "FORM VALIDATION ERROR"
            print app_form.errors
            print app_data_formset.errors
    else:
        app_form = AppForm()
        app_data_formset = App_Data_FormSet()
    
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'app_form': app_form,
         'app_data_formset': app_data_formset,
         'app_data' : simplejson.dumps(list(app_data)),
         'profile_data' : simplejson.dumps(list(profile_data)),
        }
    c.update(csrf(request))
    
    return render_to_response('app/developer/index.html', c, context_instance=RequestContext(request))


def edit(request):

    if str(request.user.profile.role) != "Developer":
        return HttpResponseRedirect('/')
    else:
        apps = App.objects.filter(author = request.user )
        return render_to_response('app/developer/edit.html', {'apps' : apps },context_instance=RequestContext(request))

def run(request):
    if str(request.user.profile.role) != "Developer":
        return HttpResponseRedirect('/')
    else:
        apps_created= App.objects.filter(author = request.user )
        
        user = UserProfile.objects.get( user_id = request.user.id )
        role_ct = ContentType.objects.get(app_label="roleapp", model="role")
        user_ct = ContentType.objects.get(app_label="auth", model="user")

        try:
            user_assigments = Assignment.objects.get(content_type_id = role_ct, object_id = user.role_id )
            apps = App.objects.filter(responsibility_id = user_assigments.Responsibility_id )
        except Exception, e:
            apps = []
        else:
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
        
        return render_to_response('app/developer/run.html', {'apps_created':apps_created,'apps':apps }, context_instance=RequestContext(request))


    
def new_domain(request):
    if request.method == 'POST': # If the form has been submitted...
        domain_form = DomainForm(request.POST) # A form bound to the POST data
        
        if domain_form.is_valid():
            domain_name = domain_form.cleaned_data['Name']
            desc = domain_form.cleaned_data['Description']
            domain_obj = Domain(Name=domain_name, Description = desc, )
            domain_obj.save()
            return HttpResponseRedirect('/apps/') # Redirect to a 'success' page
        else:
            print "FORM VALIDATION ERROR"
            return HttpResponseRedirect('/apps/domain/new')

    else:
        domain_form = DomainForm()
    
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'domain_form': domain_form,
        }
    c.update(csrf(request))
    
    return render_to_response('app/developer/domain.html', c, context_instance=RequestContext(request))


def new_app2(request):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    DataApplicationFormSet = formset_factory(DataApplicationForm2, max_num=10, formset=RequiredFormSet)

    distinct_application_outputs_objects = set()
    distinct_idle_application_inputs_objects = set()
    all_data = Data.objects.all()
    for data in all_data:
        print data
        if ( IORegistry.objects.all().filter( data_id = data.id , data_type = "Output" ).count() > 0  ): # if exist output data
            distinct_application_outputs_objects.add(data.id)

        elif ( IORegistry.objects.all().filter( data_id = data.id , idle = True ).count() > 0  ):
            distinct_idle_application_inputs_objects.add(data.id)


    idle_application_inputs = [a.get_json() for a in   Data.objects.filter(pk__in = distinct_idle_application_inputs_objects) ] 
    application_outputs = [a.get_json() for a  in  Data.objects.filter(pk__in = distinct_application_outputs_objects )] 
    user_inputs = [a.get_json() for a  in  Data.objects.filter(data_type = "User" )] 
    profile_data = UserProfile._meta.get_all_field_names()


    if request.method == 'POST': # If form has been submitted...
        main_form = AppForm2(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        formset = DataApplicationFormSet(request.POST, request.FILES)

        if main_form.is_valid() and formset.is_valid():

            app_name = main_form.cleaned_data['name']
            source = main_form.cleaned_data['source_code_host']
            resp = main_form.cleaned_data['responsibility']
            desc = main_form.cleaned_data['description']
            domain = main_form.cleaned_data['domain']
            app_obj = App(name=app_name, author=request.user, source_code_host=source, responsibility = resp, description = desc, domain = domain)
            app_obj.save()
            app_obj.source_code_host = source+'?app_id='+str(app_obj.id)
            app_obj.save()
            
            for form in formset.forms:
                data_name = form.cleaned_data['name']
                dat_type = form.cleaned_data['data_type']
                domain = form.cleaned_data['domain']
                description = form.cleaned_data['description']


                
                if ( dat_type == "User_Input"):
                    dat_type_flag = "User"
                elif( dat_type == "Profile_Input"):
                    dat_type_flag = "Profile"
                else:
                    dat_type_flag = "App"

                #counter for data with given data
                num_results = Data.objects.filter(name = data_name, data_type = dat_type_flag, domain = domain , description = description  ).count()

                # find if data already exist

                if ( num_results == 0): # if data does not exist create it
                    data_obj = Data ( name = data_name, data_type = dat_type_flag, domain = domain , description = description)
                    data_obj.save()
                else:       #if data exist give the value to data_obj
                    data_obj = Data.objects.get(name = data_name, data_type = dat_type_flag, domain = domain , description = description  )

                if ( dat_type == "Output"):
                    ioregistry_obj = IORegistry ( app = app_obj , data = data_obj, data_type = dat_type)
                    # save ioregistry object
                    ioregistry_obj.save()

                    #check if this data exist as idle input
                    if ( IORegistry.objects.filter(data = data_obj, idle = True  ).count() > 0 ):
                        # if exist update value as Not idle (because its an output) nad notify user
                        idle_objects = IORegistry.objects.filter(data = data_obj, idle = True  )
                        for idle_object in idle_objects:
                            idle_object.idle = False
                            idle_object.save()
                            app = App.objects.get ( id = idle_object.app.id )
                            print app
                            notify.send(request.user, recipient=app.author, verb='created_idle_input' , description = data_obj.name)


                else:
                    # if data is Application input and it does not exist idle = true
                    if ( num_results == 0 and dat_type == "Application_Input"):
                        idle = True
                    else:
                        idle = False

                    ioregistry_obj = IORegistry ( app = app_obj , data = data_obj, data_type = "Input", idle = idle)
                    print ioregistry_obj
                    ioregistry_obj.save()


            return HttpResponseRedirect('/apps/') # Redirect to a 'success' page
    else:
        main_form = AppForm2()
        formset = DataApplicationFormSet()

    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'main_form': main_form,
         'formset': formset,
         'profile_data' : simplejson.dumps(list(profile_data)),
         'idle_input' : simplejson.dumps(list(idle_application_inputs)),
         'output' : simplejson.dumps(list(application_outputs)),
         'user_inputs' : simplejson.dumps(list(user_inputs)),
        }
    c.update(csrf(request))

    return render_to_response('app/developer/new.html', c, context_instance=RequestContext(request))
    
def edit_specific_app(request,app_id):
	class RequiredFormSet(BaseFormSet):
		def __init__(self, *args, **kwargs):
			super(RequiredFormSet, self).__init__(*args, **kwargs)
			for form in self.forms:
				form.empty_permitted = False				

	DataApplicationFormSet = formset_factory(DataApplicationForm2, max_num=10, formset=RequiredFormSet)


	print app_id
	app = get_object_or_404(App, pk=app_id)
	print app

	form = AppForm2(instance=app)
	app_data_formset = DataApplicationFormSet(queryset=Data.objects.all())

	c = {'app_form': form,
	'app_data_formset': app_data_formset,

	}
	c.update(csrf(request))

	return render_to_response('app/developer/index.html', c, context_instance=RequestContext(request))



	 
