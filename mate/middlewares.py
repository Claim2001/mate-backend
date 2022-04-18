import pytz

from django.utils import timezone
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings


class TimezoneMiddleware(object):
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            tz_str = request.user.profile.timezone
            timezone.activate(pytz.timezone(tz_str))
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response


class NewSessionMiddleware(SessionMiddleware):

    def process_response(self, request, response):
        response = super(NewSessionMiddleware, self).process_response(request, response)
        if not request.user.is_authenticated:
            del response.cookies[settings.SESSION_COOKIE_NAME]
        return response


class DeleteCookie(object):
    def process_request(self, request, response):
        if not request.COOKIES['Auth']:
            response.delete_cookie('Auth')
            response.delete_cookie('csrftoken')
            response.delete_cookie('_fbp')
            response.delete_cookie('sessionid')
            return response
