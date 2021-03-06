from django import template
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.template import TemplateSyntaxError
from django.utils.functional import wraps
from relationships.models import RelationshipStatus
from relationships.utils import positive_filter, negative_filter
from relationships.views import get_relationship_status_or_404

register = template.Library()


class IfRelationshipNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.from_user, self.to_user, self.status = args
        self.status = self.status.replace('"', '')  # strip quotes

    def render(self, context):
        from_user = template.resolve_variable(self.from_user, context)
        to_user = template.resolve_variable(self.to_user, context)
        self.status = template.resolve_variable(self.status, context)

        if from_user.is_anonymous() or to_user.is_anonymous():
            return self.nodelist_false.render(context)

        try:
            status = RelationshipStatus.objects.by_slug(self.status)
            print "*******IfRelationshipNode***********"
            print status
        except RelationshipStatus.DoesNotExist:
            raise template.TemplateSyntaxError('RelationshipStatus not found')

        if status.from_slug == self.status:
            val = from_user.relationships.exists(to_user, status)
        elif status.to_slug == self.status:
            val = to_user.relationships.exists(from_user, status)
        else:
            val = from_user.relationships.exists(to_user, status, symmetrical=True)

        print "***** IfRelationshipNode VALUE****"
        print val

        if val:
            return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)

class IfRelationshipPossibleNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.from_user, self.to_user, self.status = args
        self.status = self.status.replace('"', '')  # strip quotes

    def render(self, context):
        #print context
        from_user = template.resolve_variable(self.from_user, context)
        to_user = template.resolve_variable(self.to_user, context)
        self.status = template.resolve_variable(self.status, context)

        print "***** IN RENR******"   
        print from_user
        print to_user
        print "temp "
        print self.status

        if from_user.is_anonymous() or to_user.is_anonymous():
            return self.nodelist_false.render(context)
        

        try:
            status = RelationshipStatus.objects.by_slug(self.status)
            print "IN IFPossible"
            print status
        except RelationshipStatus.DoesNotExist:
            print " IN DoesNotExist"
            raise template.TemplateSyntaxError('RelationshipStatus not found')
        

        print "TEST 1"
        print status.from_slug

        if status.from_slug == self.status:
            val = from_user.relationships.canexist(to_user, status)
        elif status.to_slug == self.status:
            val = to_user.relationships.canexist(from_user, status)
        else:
            val = from_user.relationships.canexist(to_user, status, symmetrical=True)

        print "*******VAL*********"
        print val

        if val:
            return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)

class HasRelationshipNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user,  self.status = args
        self.status = self.status.replace('"', '')  # strip quotes

    def render(self, context):
        user = template.resolve_variable(self.user, context)
        self.status = template.resolve_variable(self.status, context)

        if user.is_anonymous():
            return self.nodelist_false.render(context)

        try:
            status = RelationshipStatus.objects.by_slug(self.status)
        except RelationshipStatus.DoesNotExist:
            raise template.TemplateSyntaxError('RelationshipStatus not found')

        val = user.relationships.has(status)

        if val:
            return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)

class CanBeFollowedNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user,  self.status = args
        self.status = self.status.replace('"', '')  # strip quotes

    def render(self, context):
        user = template.resolve_variable(self.user, context)
        self.status = template.resolve_variable(self.status, context)

        if user.is_anonymous():
            return self.nodelist_false.render(context)

        try:
            status = RelationshipStatus.objects.by_slug(self.status)
        except RelationshipStatus.DoesNotExist:
            raise template.TemplateSyntaxError('RelationshipStatus not found')

        val = user.relationships.can_be_followed(status)

        if val:
            return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)

class CanFollowNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user,  self.status = args
        self.status = self.status.replace('"', '')  # strip quotes

    def render(self, context):
        user = template.resolve_variable(self.user, context)
        self.status = template.resolve_variable(self.status, context)

        if user.is_anonymous():
            return self.nodelist_false.render(context)

        try:
            status = RelationshipStatus.objects.by_slug(self.status)
        except RelationshipStatus.DoesNotExist:
            raise template.TemplateSyntaxError('RelationshipStatus not found')

        val = user.relationships.can_follow(status)

        if val:
            return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)


@register.tag
def if_relationship(parser, token):
    """
    Determine if a certain type of relationship exists between two users.
    The ``status`` parameter must be a slug matching either the from_slug,
    to_slug or symmetrical_slug of a RelationshipStatus.

    Example::

        {% if_relationship from_user to_user "friends" %}
            Here are pictures of me drinking alcohol
        {% else %}
            Sorry coworkers
        {% endif_relationship %}

        {% if_relationship from_user to_user "blocking" %}
            damn seo experts
        {% endif_relationship %}
    """
    bits = list(token.split_contents())
    if len(bits) != 4:
        raise TemplateSyntaxError, "%r takes 3 arguments:\n%s" % \
            (bits[0], if_relationship.__doc__)
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfRelationshipNode(nodelist_true, nodelist_false, *bits[1:])


@register.tag
def has_relationship(parser, token):
    """
    Determine if a certain type of relationship can be accessed by a user.
    The ``status`` parameter must be a slug matching either the from_slug,
    to_slug or symmetrical_slug of a RelationshipStatus.

    Example::

        {% has_relationship user "friends" %}
            Show more about it
    """
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n%s" % \
            (bits[0], if_relationship.__doc__)
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return HasRelationshipNode(nodelist_true, nodelist_false, *bits[1:])

@register.tag
def can_be_followed(parser, token):
    """
    Determine if a user can be followed according to the relationship with
    the ``status`` parameter.

    Example::

        {% can_be_followed user "follow" %}
            Show more about the relationship
    """

    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n%s" % \
            (bits[0], if_relationship.__doc__)
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return CanBeFollowedNode(nodelist_true, nodelist_false, *bits[1:])

@register.tag
def can_follow(parser, token):
    """
    Determine if a user can follow others according to the relationship with
    the ``status`` parameter.

    Example::

        {% can_be_followed user "follow" %}
            Show more about the relationship
    """

    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n%s" % \
            (bits[0], if_relationship.__doc__)
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return CanFollowNode(nodelist_true, nodelist_false, *bits[1:])

@register.tag
def if_relationship_possible(parser, token):
    """
    Determine if a certain type of relationship can exist between two users.
    The ``status`` parameter must be a slug matching either the from_slug,
    to_slug or symmetrical_slug of a RelationshipStatus.

    Example::

        {% if_relationship_possible from_user to_user "friends" %}
            Here are pictures of me drinking alcohol
        {% else %}
            Sorry coworkers
        {% endif_relationship %}

        {% if_relationship from_user to_user "blocking" %}
            damn seo experts
        {% endif_relationship %}
    """
    bits = list(token.split_contents())
    print bits
    
    if len(bits) != 4:
        raise TemplateSyntaxError, "%r takes 3 arguments:\n%s" % \
            (bits[0], if_relationship.__doc__)
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    print "------ IN if_relationship_possible-------"
    print nodelist_false
    print nodelist_true
    return IfRelationshipPossibleNode(nodelist_true, nodelist_false, *bits[1:])


@register.filter
def add_relationship_url(user, status):
    """
    Generate a url for adding a relationship on a given user.  ``user`` is a
    User object, and ``status`` is either a relationship_status object or a
    string denoting a RelationshipStatus

    Usage::

        href="{{ user|add_relationship_url:"following" }}"
    """
    if isinstance(status, RelationshipStatus):
        status = status.from_slug
    return reverse('relationship_add', args=[user.username, status])


@register.filter
def remove_relationship_url(user, status):
    """
    Generate a url for removing a relationship on a given user.  ``user`` is a
    User object, and ``status`` is either a relationship_status object or a
    string denoting a RelationshipStatus

    Usage::

        href="{{ user|remove_relationship_url:"following" }}"
    """
    if isinstance(status, RelationshipStatus):
        status = status.from_slug
    return reverse('relationship_remove', args=[user.username, status])


@register.filter
def remove_relationship(user, status):
    """
    Generate a url for removing a relationship on a given user.  ``user`` is a
    User object, and ``status`` is either a relationship_status object or a
    string denoting a RelationshipStatus

    Usage::

        href="{{ user|remove_relationship_url:"following" }}"
    """
    if isinstance(status, RelationshipStatus):
        status_slug = status.from_slug
    else: 
        status_slug = status
    status = get_relationship_status_or_404(status_slug)
    is_symm = status_slug == status.symmetrical_slug
    user.relationships.remove(user, status, is_symm)
    return 


def positive_filter_decorator(func):
    def inner(qs, user):
        if isinstance(qs, basestring):
            model = get_model(*qs.split('.'))
            if not model:
                return []
            qs = model._default_manager.all()
        if user.is_anonymous():
            return qs.none()
        return func(qs, user)
    inner._decorated_function = getattr(func, '_decorated_function', func)
    return wraps(func)(inner)


def negative_filter_decorator(func):
    def inner(qs, user):
        if isinstance(qs, basestring):
            model = get_model(*qs.split('.'))
            if not model:
                return []
            qs = model._default_manager.all()
        if user.is_anonymous():
            return qs
        return func(qs, user)
    inner._decorated_function = getattr(func, '_decorated_function', func)
    return wraps(func)(inner)


@register.filter
@positive_filter_decorator
def friend_content(qs, user):
    return positive_filter(qs, user.relationships.friends())


@register.filter
@positive_filter_decorator
def following_content(qs, user):
    return positive_filter(qs, user.relationships.following())


@register.filter
@positive_filter_decorator
def followers_content(qs, user):
    return positive_filter(qs, user.relationships.followers())


@register.filter
@negative_filter_decorator
def unblocked_content(qs, user):
    return negative_filter(qs, user.relationships.blocking())
