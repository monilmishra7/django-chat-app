from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ChatRoom, Message
from django.contrib.auth.views import LoginView
from django.contrib.sessions.models import Session
from django.utils import timezone


class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('chat:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        Session.objects.filter(
            expire_date__gt=timezone.now()
        ).filter(
            session_data__contains=str(user.id)
        ).delete()
        
        return super().form_valid(form)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/index.html', {'users': users})

@login_required
def room(request, user_id):
    chat_user = User.objects.get(id=user_id)
    users = User.objects.exclude(id=request.user.id)
    
    # Get or create chat room
    room = ChatRoom.objects.filter(participants=request.user)\
                          .filter(participants=chat_user)\
                          .first()
                          
    if not room:
        room = ChatRoom.objects.create()
        room.participants.add(request.user, chat_user)
    
    # Get messages
    messages = Message.objects.filter(room=room).order_by('timestamp')
    
    return render(request, 'chat/room.html', {
        'chat_user': chat_user,
        'users': users,
        'room': room,
        'messages': messages
    })