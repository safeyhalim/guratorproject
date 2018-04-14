#automatic Django administrative interface
from django.contrib import admin
from .models import Participant, PersonalityQuestion

# Register your models here.

admin.site.register(Participant)
admin.site.register(PersonalityQuestion)
