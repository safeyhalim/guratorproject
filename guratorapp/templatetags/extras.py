#used to generate html dynamically
from django import template
#provides some additional low level utilities for escaping HTML
from django.utils.html import conditional_escape
#easy way to get groups
from django.contrib.auth.models import Group
#Explicitly mark a string as safe for (HTML) output purposes. The returned object can be used everywhere a string is appropriate.
from django.utils.safestring import mark_safe

#To be a valid tag library, the module must contain a module-level variable named register that is a template.Library instance, in which all the tags and filters are registered
register = template.Library()

@register.filter(name='get_image_path')
def get_image_path(value):
    g = value.split("/")
    l = g[len(g) - 1]

    if len(l) == 0:
        l = "default.jpg"
    return "/static/img/" + str(l)

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False
