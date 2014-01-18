from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from django.contrib import admin
admin.autodiscover()

from api import * #RoleTypeResource, UserProfileResource, UserResource, RelationshipStatusResource, RelationshipResource, AppStreamResource, AppDataResource, AppResource, ContentTypeResource


rest = Api(api_name='v1')
rest.register(UserResource())
rest.register(RoleTypeResource())
rest.register(UserProfileResource())
rest.register(RelationshipStatusResource())
rest.register(RelationshipResource())
rest.register(AppStreamResource())
rest.register(AppDataResource())
rest.register(AppResource())
rest.register(ContentTypeResource())
rest.register(ActionStreamResource())


#role_resource = RoleTypeResource()
#user_resource = UserProfileResource()


urlpatterns = patterns('',
    # url(r'^catalog/', include('catalog.foo.urls')),

    url(r'^rest/', include(rest.urls)),
    #url(r'^users/', include(user_resource.urls)),
)
