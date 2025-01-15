from django.utils import timezone
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == reverse('login') and request.user.is_authenticated:
            return redirect('chat:index')

        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            
            # Only get sessions for the CURRENT user
            user_sessions = Session.objects.filter(
                expire_date__gt=timezone.now()
            ).filter(
                session_data__contains=f'"_auth_user_id":"{request.user.id}"'
            ).exclude(
                session_key=current_session_key  # Exclude current session
            )

            # Log for debugging
            logger.info(f"User {request.user.username} (ID: {request.user.id})")
            logger.info(f"Current session: {current_session_key}")
            logger.info(f"Found {user_sessions.count()} other sessions")

            # Delete other sessions for this user only
            if user_sessions.exists():
                user_sessions.delete()
                logger.info("Deleted other sessions for this user")

        response = self.get_response(request)
        return response