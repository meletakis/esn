from django.contrib.auth.models import User
from tastypie import fields
from notifications.models import Notification
from relationships.models import RelationshipStatus, Relationship
from extendedmodelresource import ExtendedModelResource


class UserExtendedResource(ExtendedModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

    class Nested:
        notifications = fields.ToManyField('api.resources.ExtendedNotificationResource', 'notifications')
        relationships = fields.ToManyField('api.resources.ExtendedRelationshipResource', 'relationships')


class ExtendedNotificationResource(ExtendedModelResource):
    recipient = fields.ForeignKey(UserExtendedResource, 'recipient')

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'

class ExtendedRelationshipResource(ExtendedModelResource):
    from_user = fields.ForeignKey(UserExtendedResource, 'from_user',full=True,null=True)


    class Meta:
        queryset = Relationship.objects.all()
        resource_name = 'relationship'

    class Nested:
        relationship_status = fields.OneToManyField('api.resources.ExtendedRelationshipStatusResource', 'relationship_status')      


class ExtendedRelationshipStatusResource(ExtendedModelResource):
    class Meta:
        queryset = RelationshipStatus.objects.all()
        resource_name = 'relationship_status'






"""
class EntryInfoResource(ExtendedModelResource):
    class Meta:
        queryset = EntryInfo.objects.all()
        resource_name = 'EntryInfo'


class UserByNameResource(ExtendedModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'userbyname'
        detail_uri_name = 'username'

    def get_url_id_attribute_regex(self):
        # The id attribute respects this regex.
        return r'[aA-zZ][\w-]*'
"""