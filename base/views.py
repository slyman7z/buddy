from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout ,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
'''rooms = [
    {'id':1, 'name':'Lets learn Python'},
    {'id':2, 'name': 'Design with me'},
    {'id':3, 'name': 'frontend developers'},
] '''

def loginPage(request):

    page = 'login'          #to display whether a user already has an account

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()    #Get username 
        password = request.POST.get('password')     #Get password
        try:
            user = User.objects.get(username =  username)
        except:
            messages.error(request, 'Username does not exist')  #Check if user exist

        user = authenticate(request, username = username, password= password)   #check username and password  are correct and get username and password

        if user is not None:                # login user
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist') # else display error message

    context= {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error during registration')


    context = {'form': form}
    return render(request, 'base/registerpage.html', context)
    


@login_required(login_url='login')     # a user has to be logged in to view this page
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # search value is returned
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)
        
        )
    topics = Topic.objects.all()
    room_count = rooms.count


    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count
    
    
    
    }
    return render(request, 'base/home.html', context)

@login_required(login_url='login') # a user has to be logged in to view this page
def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.messages_set.all().order_by('-created')

    context = {
        'room':room,
        'room_messages': room_messages,
    
    }
    return render(request,'base/room.html', context)

@login_required(login_url='login') # a user has to be logged in to view this page
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'form': form
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') # a user has to be logged in to view this page
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form  = RoomForm(instance=room)

    if request.user != room.host:                           # a user cant modify another users page
        return HttpResponse('You are not authorised')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance= room)
        if form.is_valid():
            form.save()
            return redirect ('home')
    

    context={'form': form }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')     # a user has to be logged in to view this page
def delete(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:                           # a user cant modify another users page
        return HttpResponse('You are not authorised')

    if request.method == 'POST':
        room.delete()
        return redirect ('home')

    context = {'obj': room}
    return render (request, 'base/delete.html', context)


