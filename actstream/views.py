# coding: utf-8
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from organizations.models import Organization
from actstream import actions, models, compat, action
from actstream.forms import Wall_Post_Form, Group_Post_Form
from actstream.models import Action
from userprofiles.models import UserProfile
from relationships.models import RelationshipStatus, Relationship
from userprofiles.models import freeCrop
from userprofiles.models import uploadedImage
from organizations.models import OrganizationUser
from django.db.models import Q
from itertools import chain
User = compat.get_user_model()
from notifications import notify
from django.shortcuts import redirect
from urlparse import urlparse
from django.conf import settings
import opengraph
import re
import urllib
import urlparse 
import httplib
import operator
import time

def respond(request, code):
    """
    Responds to the request with the given response code.
    If ``next`` is in the form, it will redirect instead.
    """
    if 'next' in request.REQUEST:
        return HttpResponseRedirect(request.REQUEST['next'])
    return type('Response%d' % code, (HttpResponse, ), {'status_code': code})()


@login_required
@csrf_exempt
def follow_unfollow(request, content_type_id, object_id, do_follow=True, actor_only=True):
    """
    Creates or deletes the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)

    if do_follow:
        actions.follow(request.user, actor, actor_only=actor_only)
        return respond(request, 201)   # CREATED
    actions.unfollow(request.user, actor)
    return respond(request, 204)   # NO CONTENT


@login_required
def stream(request, template='actstream/actor.html', page_template='actstream/action.html'):
	"""
	Index page for authenticated user's activity stream. (Eg: Your feed at
	github.com)
	"""
	viewer = request.user
	viewer_user_role = UserProfile.objects.get( user_id = viewer.id )
	posts_set =[]
	posts_final = []
	posts_set_ids = []
	posts_set_ids_m =[]
	posts_set_by_user =[]
	posts_final_by_other_users = []
	posts_set_user_ids = []
	posts_final_mentioned_for_this_user =[]
	group_actions_list = []
	
	user_ct = ContentType.objects.get(app_label="auth", model="user") # User Content Type
	
	######## posts by owner #########
	posts_set_user_distinct = list (Action.objects.filter( Q(verb='posted' ) & Q(actor_object_id = viewer.id) & Q(actor_content_type_id = user_ct.id) ).values_list('timestamp').distinct())
	for y in Action.objects.filter(verb='posted'):
			for x in posts_set_user_distinct:
				if y.timestamp ==x[0]:
					posts_set_user_distinct.remove(x)
					posts_set_user_ids.append(y.id)
				
	for wp_id in posts_set_user_ids:
		posts_set_by_user.extend(Action.objects.filter( id = wp_id ) )
		
	
	relation_ct = ContentType.objects.get(app_label="relationships", model="relationshipstatus") # User Content Type
	
	##########posts by other related users ######
	for related_users in Relationship.objects.all().filter(from_user_id = viewer.id ):
		actions_list = Action.objects.filter( Q(verb='posted' ) & Q(actor_object_id = related_users.to_user_id )  & Q(target_object_id = related_users.status_id) & Q(actor_content_type_id = user_ct.id) & Q(target_content_type_id = relation_ct.id))
		posts_set_distinct = list ( actions_list.values_list('timestamp').distinct())
		for y in Action.objects.filter( Q(verb='posted' ) &  ( Q(actor_object_id = related_users.to_user_id) ) & Q(target_object_id = related_users.status_id) & Q(actor_content_type_id = user_ct.id) & Q(target_content_type_id = relation_ct.id) ):
			for x in posts_set_distinct:
				if y.timestamp ==x[0]:
					posts_set_distinct.remove(x)
					posts_set_ids.append(y.id)
					
		for wp_id in posts_set_ids:
			posts_final_by_other_users.extend(Action.objects.filter( id = wp_id ) )
			
		posts_set_ids =[]
	print "OTHER"
	print posts_final_by_other_users
			
	##########posts mentioned to user ######
	posts_set_user_ids = []
	posts_set_for_mentioned_user_distinct = list (Action.objects.filter( Q(verb='posted' ) & Q(target_object_id = viewer.id) & Q(actor_content_type_id = user_ct.id) & Q(target_content_type_id = user_ct.id) ).values_list('timestamp').distinct())
	for y in Action.objects.filter(verb='posted'):
			for x in posts_set_for_mentioned_user_distinct:
				if y.timestamp ==x[0]:
					posts_set_for_mentioned_user_distinct.remove(x)
					posts_set_user_ids.append(y.id)
				
	for wp_id in posts_set_user_ids:
		posts_final_mentioned_for_this_user.extend(Action.objects.filter( id = wp_id ) )
		
		
	##########posts from groups ######
	organization_ct = ContentType.objects.get(app_label="organizations", model="organization")	
	for related_groups in OrganizationUser.objects.all().filter(user_id = viewer.id ):
		group_actions_list.extend (Action.objects.filter( Q(verb='posted' ) & ~Q(actor_object_id = viewer.id )  & Q(target_object_id = related_groups.organization_id) & Q(actor_content_type_id = user_ct.id) & Q(target_content_type_id = organization_ct.id)))
		
	print "OTHER"
	print group_actions_list
	
	related_org =[]
	for related_org_user in OrganizationUser.objects.all().filter(user_id = viewer.id ):
		related_org.extend(Organization.objects.all().filter(id = related_org_user.organization_id ))
	print "RELATED GROUPS"
	print related_org
	
	
	posts_final = posts_final_by_other_users+ posts_set_by_user + posts_final_mentioned_for_this_user + group_actions_list
	print posts_final
	posts_final.sort(key=lambda Action	: Action.timestamp, reverse= True)# sort actions by timestamp


	users = User.objects.all()
	suggested_users = []
	contacts = []
	user_relationships = RelationshipStatus.objects.all().filter( to_role_id = request.user.profile.role.id )
	for status in user_relationships:
		contacts.extend(request.user.relationships.get_related_to(status=status))
	users = list(set(users)^set(contacts))
	for user in users:
		
		if not user.is_superuser and user != request.user:
			common_activities = list(set(user.profile.activities.all()).intersection(request.user.profile.activities.all()))
			if len(common_activities) >= 3:
				suggested_users.append(user)
			else:
				if len(common_activities) == 2:
					if user.profile.studies == request.user.profile.studies:					
						suggested_users.append(user)
					else:
						if user.profile.status == request.user.profile.status:
							suggested_users.append(user)
				else:
					if len(common_activities) == 1:
						if user.profile.status == request.user.profile.status or user.profile.studies == request.user.profile.studies:
							suggested_users.append(user)


	'''
	return render_to_response(('actstream/actor.html', 'activity/actor.html'), {
	'ctype': ContentType.objects.get_for_model(User),
	'actor': request.user, 'action_list': posts_final, 'related_groups':related_org, 'users':suggested_users, 'username':request.user.username
	}, context_instance=RequestContext(request))
	'''
	iform = freeCrop(request.POST)
	context =  {
	'ctype': ContentType.objects.get_for_model(User),
	'actor': request.user, 
	'action_list': posts_final, 
	'related_groups':related_org,
	'page_template': page_template,
	'users':suggested_users,
	'image_form':iform,
	'username':request.user.username,
	'contacts':contacts
	}
	
	if request.is_ajax():
		template = page_template
	return render_to_response(template, context, context_instance=RequestContext(request))	




def followers(request, content_type_id, object_id):
    """
    Creates a listing of ``User``s that follow the actor defined by
    ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)
    return render_to_response(('actstream/followers.html', 'activity/followers.html'), {
        'followers': models.followers(actor), 'actor': actor
    }, context_instance=RequestContext(request))


def following(request, user_id):
    """
    Returns a list of actors that the user identified by ``user_id`` is following (eg who im following).
    """
    user = get_object_or_404(User, pk=user_id)
    return render_to_response(('actstream/following.html', 'activity/following.html'), {
        'following': models.following(user), 'user': user
    }, context_instance=RequestContext(request))


def user(request, username):
    """
    ``User`` focused activity stream. (Eg: Profile page twitter.com/justquick)
    """
    user = get_object_or_404(User, username=username, is_active=True)
    return render_to_response(('actstream/actor.html', 'activity/actor.html'), {
        'ctype': ContentType.objects.get_for_model(User),
        'actor': user, 'action_list': models.user_stream(user)
    }, context_instance=RequestContext(request))


def detail(request, action_id):
    """
    ``Action`` detail view (pretty boring, mainly used for get_absolute_url)
    """
    return render_to_response(('actstream/detail.html', 'activity/detail.html'), {
        'action': get_object_or_404(models.Action, pk=action_id)
    }, context_instance=RequestContext(request))


def actor(request, content_type_id, object_id):
    """
    ``Actor`` focused activity stream for actor defined by ``content_type_id``,
    ``object_id``.
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)
    return render_to_response(('actstream/actor.html', 'activity/actor.html'), {
        'action_list': models.actor_stream(actor), 'actor': actor,
        'ctype': ctype
    }, context_instance=RequestContext(request))


def model(request, content_type_id):
    """
    ``Actor`` focused activity stream for actor defined by ``content_type_id``,
    ``object_id``.
    """
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = ctype.model_class()
    return render_to_response(('actstream/actor.html', 'activity/actor.html'), {
        'action_list': models.model_stream(actor), 'ctype': ctype,
        'actor': actor
    }, context_instance=RequestContext(request))
    
    
    
def rendered_content( content,request ):
#for wall_post in wall_posts:
	title = ''
	desc = ''
	site_image = ''
	article_title = ''
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
	mentions = re.findall('\@\w+', content)
	r = re.compile('###uploaded_image###(.*?)##!uploaded_image!##')
	m = r.search(content)
	if m:
		content = content.replace(m.group(1), "").replace("###uploaded_image###", "").replace("##!uploaded_image!##", "") +"<br/><div class='row'><div class='col-sm-6 col-md-3'><a href='"+m.group(1)+"' target='_blank' class='thumbnail'><img data-src='holder.js/300' src='"+m.group(1)+"'/></a></div></div>"
	
	for mention in mentions:
		mentioned_username= mention.replace('@','')
		mentioned_user = User.objects.get(username=mentioned_username)
		if mentioned_user:
			notify.send(request.user, recipient=mentioned_user, verb='post_mention' )
			content=content.replace(mention, '<a href="/user/profile/'+mentioned_username+'">'+mention+'</a>')	
	for url in urls: 
		parse_obj = urlparse.urlparse(url)
		site = parse_obj.netloc
		path = parse_obj.path
		conn = httplib.HTTPConnection(site)
		conn.request('HEAD',path)
		response = conn.getresponse()
		conn.close()
		ctype = response.getheader('Content-Type')
		if response.status < 400 and ctype.startswith('image'):
			content = content+"<br/><div class='row'><div class='col-sm-6 col-md-3'><a href='"+url+"' target='_blank' class='thumbnail'><img data-src='holder.js/300' src='"+url+"'/></a></div></div>"
		else:
			og = opengraph.OpenGraph(url)
			if not len(og.items()) == 2:
				for x,y in og.items():
					if x == 'type' and y == 'video':
						for k,l in og.items():
							if k == 'site_name' and l == 'YouTube':
						
								url_data = urlparse.urlparse(url)
								query = urlparse.parse_qs(url_data.query)
								video = query["v"][0]
								content = content.replace(url,"<a href='"+url+"' target='_blank'>"+url+"</a>")+"<br/><br/><iframe width='300' height='200' src='//www.youtube.com/embed/"+video+"' frameborder='0' allowfullscreen></iframe>"
							elif k == 'site_name' and l == 'Vimeo':
								url_data = urlparse.urlparse(url)
								video = url_data.path
								content = content.replace(url,"<a href='"+url+"' target='_blank'>"+url+"</a>")+"<br/><br/><iframe src='//player.vimeo.com/video"+video+"' width='300' height='200' frameborder='0' webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <p></p>"
					elif x == 'type' and y == 'article':
						for k,l in og.items():
							if k == 'title':
								article_title = l
							elif k == 'site_name':
								title = l
							elif k=='description':
								desc = l
							elif k=='image':
								site_image = l
						content = content +"<br/><table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+article_title+"</a><br/>"+title+"</td></td></table>"
					elif x=='type':
						for k,l in og.items():
							if k == 'site_name':
								title = l
							elif k=='description':
								desc = l
							elif k=='image':
								site_image = l
						content = content.replace(url, "<table><tr><td><img width='50' src='"+site_image+"'</td><td><a href='"+url+"' target='_blank'/>"+title+"</a><br/>"+desc+"</td></td></table>")
			else:
				content = content.replace(url, "<a href='"+url+"' target='_blank'>"+url+"</a>")	

	return content
    
def new_wall_post (request):
	image_url = ""
	viewer = request.user
	owner_user = request.user
	owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
	if request.method == 'POST':
		form = freeCrop(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
		    	new_event = form.save()
		    	#return HttpResponseRedirect('/user/profile/'+request.user.username)
		    	#return HttpResponseRedirect('/file-upload/cicu-freecrop/?id='+str(new_event.id))
			a = new_event.id
			if uploadedImage.objects.get(id=a).image:
				image_url = "###uploaded_image###"+uploadedImage.objects.get(id=a).image.url+"##!uploaded_image!##"
			
		form = Wall_Post_Form(request.POST)
		if form.is_valid():
			content = form.cleaned_data['content']
			if content != "" or image_url!="":
				content = content + image_url
				actor_name = form.cleaned_data['actor_name']
				post_target = form.cleaned_data['target']
				#####################
				owner_user = User.objects.get(username__exact = actor_name) # user creation
				owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
				#relationships =  [relationship for relationship in RelationshipStatus.objects.all().filter (to_role_id = user_role.role_id)]
			
				content = rendered_content (content,request)
			
			
				if post_target == "Private":
					print "Private target"
					action.send(viewer, verb='posted', action_object = owner_user, target= viewer,  post_content=content) # action creation
				elif post_target == "Public":
					print "public target"
					print owner_user_role.role_id
					for relationship in RelationshipStatus.objects.all().filter (to_role_id = owner_user_role.role_id):
						action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content) # action creation
				else:
					for relationship in RelationshipStatus.objects.all().filter (Q(to_role_id = owner_user_role.role_id) & Q(name = post_target )):
						action.send(viewer, verb='posted', action_object = owner_user, target=relationship,  post_content=content) # action creation
			
				# notification NOT USED
				'''
				if request.user.id != user.id:
					print user.id
					notify.send(request.user,  recipient=user, verb='wall_post' )
				'''
		else:
			print "ERROR IN VALIDATION"
			print form.errors		
	else:
		form = Wall_Post_Form()
		
	return HttpResponseRedirect('/user/profile/'+request.user.username)
	
def get_actions_by_user( viewer, owner ):
	wall_posts = []
	wall_posts_ids = []
		# Viewer is owner
	if viewer == owner:
		wall_posts_distinct = list (Action.objects.filter( Q (action_object_object_id = owner.id ) & Q(verb='posted')).values_list('timestamp').distinct())# all distinct wall posts
		for y in Action.objects.filter(verb='posted'):
			for x in wall_posts_distinct:
				if y.timestamp ==x[0]:
					wall_posts_distinct.remove(x)
					wall_posts_ids.append(y.id)
				
		for wp_id in wall_posts_ids:
			wall_posts.extend(Action.objects.filter( id = wp_id ) )
	else:
		# Collect users role
		owner_user_role = UserProfile.objects.get( user_id = owner.id )
		viewer_user_role = UserProfile.objects.get( user_id = viewer.id )
		
		for relationship_status in RelationshipStatus.objects.all().filter( Q(to_role_id = owner_user_role.role_id) & Q(from_role_id = viewer_user_role.role_id)):
			if relationship_status:
				print relationship_status.id
				if Relationship.objects.all().filter( Q(to_user_id = owner.id) & Q(from_user_id = viewer.id) & Q(status_id = relationship_status.id) ).exists():
					wall_posts = Action.objects.filter( Q(verb='posted' ) & Q(target_object_id = relationship_status.id) & Q(action_object_object_id = owner.id))
					#wall_posts = Action.objects.filter(target_object_id = relationship_status.id)
					#wall_posts = Action.objects.filter(action_object_object_id = owner.id)					
					
					print "RELATIONSHIP EXIST"
				else:
					print "NO RELATIONSHIP"
			else:
				print " NO RELATIONSHIP"
				
	return wall_posts

def new_group_post (request):
	image_url=''
	viewer = request.user
	owner_user = request.user
	owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
	if request.method == 'POST':
		eform = freeCrop(request.POST) # A form bound to the POST data
		if eform.is_valid(): # All validation rules pass
		    	new_event = eform.save()
		    	#return HttpResponseRedirect('/user/profile/'+request.user.username)
		    	#return HttpResponseRedirect('/file-upload/cicu-freecrop/?id='+str(new_event.id))
			a = new_event.id
			if uploadedImage.objects.get(id=a).image:
				image_url = "###uploaded_image###"+uploadedImage.objects.get(id=a).image.url+"##!uploaded_image!##"
		form = Group_Post_Form(request.POST)
		if form.is_valid():
			######## form values ###########
			content = form.cleaned_data['content']+image_url
			actor_name = form.cleaned_data['actor_name']
			group_id = form.cleaned_data['group_id']
			#####################			
			owner_user_role = UserProfile.objects.get( user_id = owner_user.id )
			org = Organization.objects.get( id = group_id )
			content = rendered_content (content,request)
			action.send(viewer, verb='posted', action_object = org, target= org,  post_content=content) # action creation
		else:
			print "ERROR IN VALIDATION"
			print form.errors		
	else:
		form = Group_Post_Form()

	return HttpResponseRedirect('/groups/'+group_id)


