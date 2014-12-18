from tastypie.authorization import Authorization


class UserResourceAuthorization(Authorization):
    """
    Our Authorization class for UserResource and its nested.
    """

    def is_authorized(self, request, object=None):
        # Only 'newton' is authorized to view the users
          return True


    def apply_limits(self, request, object_list):
        return object_list.all()
