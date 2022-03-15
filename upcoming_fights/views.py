from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from upcoming_fights.models import Fighter, Follow, UpcomingFight
from django.template import RequestContext
from django.views.generic import ListView



def index(request):

    return render(request, 'upcoming_fights/index.html')


def followed_fighters(request):

    template_name = 'upcoming_fights/followed_fighters.html'
    followed_objects = Follow.objects.filter(user = request.user)
    followed_fighters = []
    for object in followed_objects:
        followed_fighters.append(object.fighter)
    
    upcoming_fights = UpcomingFight.objects.all()

    return render(request, template_name, {'followed_fighters': followed_fighters, 'upcoming_fights': upcoming_fights})


def get_fighter_list(max_results=0, contains=''):
    fighter_list = []
    if contains:
        fighter_list = Fighter.objects.filter(name__icontains=contains)
    
    if max_results > 0:
        if len(fighter_list) > max_results:
            fighter_list = fighter_list[:max_results]
    return fighter_list


def search_fighters(request):
    fighter_list = []
    contains = ''

    if request.method == 'GET':
        if 'query' in request.GET:
            contains = request.GET['query']
        else:
            contains = ''
    fighter_list = get_fighter_list(100, contains)

    followed_objects = Follow.objects.filter(user = request.user)
    followed_fighters = []
    for object in followed_objects:
        followed_fighters.append(object.fighter)

    return render(request, 'upcoming_fights/search_fighters2.html', {'fighters': fighter_list, 'following': followed_fighters})

def trending_fighters(request):
    fighter_list = Fighter.objects.filter(followers__gte=1).order_by('-followers')[:100]
    
    followed_objects = Follow.objects.filter(user = request.user)
    followed_fighters = []
    for object in followed_objects:
        followed_fighters.append(object.fighter)
    
    return render(request, 'upcoming_fights/trending.html', {'fighters': fighter_list, 'following': followed_fighters})


@login_required
def follow_fighter(request):
    f_id = None
    if request.method == 'GET':
        f_id = request.GET['fighter_id']

    if f_id:
        fighter = Fighter.objects.get(fighter_id=f_id)

        if fighter:
            if fighter.is_first_follow():
                fighter.new_follow_find_upcoming_fight()
            Follow.objects.get_or_create(user = request.user, fighter = fighter)
            fighter.followers += 1
            fighter.save()


    return HttpResponse()

@login_required
def unfollow_fighter(request):
    f_id = None
    if request.method == 'GET':
        f_id = request.GET['fighter_id']

    if f_id:
        fighter = Fighter.objects.get(fighter_id=f_id)

        if fighter:
            follow = Follow.objects.get(user = request.user, fighter = fighter)
            follow.delete()
            fighter.followers -= 1
            fighter.save()

    return HttpResponse()