from atexit import register
from django import template
from upcoming_fights.models import Fighter, Follow

register = template.Library()

@register.inclusion_tag('upcoming_fights/fighters.html', takes_context=True)
def get_fighter_list(context):
    user = context['user']
    following_objects = Follow.objects.filter(user = user)
    following_fighter = []
    for object in following_objects:
        following_fighter.append(object.fighter)

    fighters = Fighter.objects.all()[:5]
        
    return {'fighters': fighters, 'following': following_fighter, 'user': user}