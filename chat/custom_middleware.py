from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import redirect
from django.urls import reverse

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If this is the login page and user is already authenticated
        if request.path == reverse('login') and request.user.is_authenticated:
            # Redirect to home page
            return redirect('chat:index')
            
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            
            # Get all sessions for current user
            active_sessions = Session.objects.filter(
                expire_date__gt=timezone.now()
            ).values_list('session_key', flat=True)
            
            user_sessions = []
            for session_key in active_sessions:
                session_data = SessionStore(session_key=session_key)
                if str(request.user.id) == str(session_data.get('_auth_user_id')):
                    user_sessions.append(session_key)

            # If there are other sessions and this isn't a logout request
            if len(user_sessions) > 1 and not request.path == reverse('logout'):
                # Delete other sessions
                for session_key in user_sessions:
                    if session_key != current_session_key:
                        Session.objects.filter(session_key=session_key).delete()

        response = self.get_response(request)
        return response