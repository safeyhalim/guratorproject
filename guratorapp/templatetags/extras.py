from django import template
from django.utils.html import conditional_escape
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

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

