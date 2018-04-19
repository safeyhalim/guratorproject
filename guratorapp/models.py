from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django_countries import countries


def content_file_name(instance, filename):
    if filename.find("."):
        return instance.user.username + filename[filename.find("."):]
    else:
        return instance.user.username


class PersonalityQuestion(models.Model):
    name = models.CharField(max_length=10, default='no name')
    optionA = models.CharField(max_length=1000, verbose_name="A")
    optionB = models.CharField(max_length=1000, verbose_name="B")

    def __unicode__(self):
        return self.name


class Participant(models.Model):
    GENDER_CHOICES = (
        ('f', 'female'),
        ('m', 'male'),
    )
    
    name = models.CharField(max_length=500, verbose_name="Username")
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    real_name = models.CharField(max_length=50, verbose_name="Real name")
    email = models.CharField(max_length=500, verbose_name="E-Mail address", default="")
    email2 = models.CharField(max_length=500, verbose_name="E-Mail address (confirmation)", default="")
    accepted_terms_conditions = models.BooleanField(default=False, verbose_name="I accept the terms and conditions as stated above")
    ip = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=2, verbose_name="Gender", choices=GENDER_CHOICES)
    picture = models.ImageField(upload_to=content_file_name, blank=True, verbose_name="Profile picture")
    birthdate = models.DateField(verbose_name="Date of Birth", default="")
    country = CountryField(choices=list(countries), verbose_name="Country", default=countries.name('DE'))
    matriculation_number = models.CharField(max_length=10, default="0")
    gps_long = models.CharField(max_length=15)
    gps_lat = models.CharField(max_length=15)
    grade = models.CharField(max_length=5)
    personality_answers = models.ManyToManyField(PersonalityQuestion,
                                                 through="ParticipantPersonalityQuestion",
                                                 through_fields=("participant", "personality_question"))
    groups = models.ManyToManyField("Group", through="GroupParticipant", through_fields=("participant", "group"))
    personality_test_done = models.BooleanField(default=False, verbose_name="Personality test done")
    # my code
    personality_competing = models.IntegerField(default=0)
    personality_cooperating = models.IntegerField(default=0)
    personality_compromising = models.IntegerField(default=0)
    personality_avoiding = models.IntegerField(default=0)
    personality_accommodating = models.IntegerField(default=0)
    # end of my code

    def __unicode__(self):
        return self.name


class ParticipantPersonalityQuestion(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    personality_question = models.ForeignKey(PersonalityQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=2, choices=(('A', 'Option A'), ('B', 'Option B')))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.participant.name + ":" + self.personality_question.optionA + "/" + self.personality_question.optionB + ":" + self.answer


class UserSurvey(models.Model):
    from_participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="from_participant")
    to_participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="to_participant")
    relationship = models.CharField(max_length=50, default="N/A")
    social_capital = models.IntegerField(default=0)
    tie_strength = models.IntegerField(default=0)
    social_similarity = models.IntegerField(default=0)
    social_context_similarity = models.IntegerField(default=0)
    sympathy = models.IntegerField(default=0)
    social_hierarchy = models.IntegerField(default=0)
    domain_expertise = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)    
        
    def __unicode__(self):
        return "From participant:" + self.from_participant.name + " to participant:" + self.to_participant.name + " Social capital = " + self.social_capital + " Tie strength = " + self.tie_strength + " Social similarity = " + self.social_similarity + " Social context similarity = " + self.social_context_similarity + " Sympathy = " + self.sympathy + " Social Hierarchy = " + self.social_hierarchy + " Domain Expertise = " + self.domain_expertise
    

class RestaurantSurvey(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="participant_rating_the_restaurant")
    restaurant_id = models.CharField(max_length=100, blank=False)
    price = models.IntegerField(default=0)
    taste = models.IntegerField(default=0)
    clumsiness = models.IntegerField(default=0)
    service = models.IntegerField(default=0)
    #hippieness = the state or quality of being a hippy or hippies
    hippieness = models.IntegerField(default=0)
    location = models.IntegerField(default=0)
    social_overlap = models.IntegerField(default=0)
    other = models.CharField(max_length=1000, blank=True)
    
    def __unicode__(self):
        return "Rating of participant" + self.participant + " to restaurant:" + self.resturant_id + ": price = " + self.price + " taste = " + self.taste + " clumsiness = " + self.clumsiness + " service = " + self.service + " hippieness = " + self.hippieness + " location = " + self.location + " social overlap = " + self.social_overlap + " other = " + self.other


class GroupRestaurantSurvey(models.Model):
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="group_rating_the_restaurant")
    restaurant_id = models.CharField(max_length=100, blank=False)
    price = models.IntegerField(default=0)
    taste = models.IntegerField(default=0)
    clumsiness = models.IntegerField(default=0)
    service = models.IntegerField(default=0)
    hippieness = models.IntegerField(default=0)
    location = models.IntegerField(default=0)
    social_overlap = models.IntegerField(default=0)
    other = models.CharField(max_length=1000, blank=True)
    
    def __unicode__(self):
        return "Rating of group" + self.group + " to restaurant:" + self.resturant_id + ": price = " + self.price + " taste = " + self.taste + " clumsiness = " + self.clumsiness + " service = " + self.service + " hippieness = " + self.hippieness + " location = " + self.location + " social overlap = " + self.social_overlap + " other = " + self.other
    

class Group(models.Model):
    name = models.CharField(max_length=20)
    creator = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="group_creator")
    participants = models.ManyToManyField(Participant, through="GroupParticipant", through_fields=("group", "participant"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True) 
    
    def __unicode__(self):
        return "Group " + self.group_name + " created by: " + self.creator + "on " + self.created

class GroupParticipant(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "Participant " + self.participant.name + " member of group " + self.group.name + " since " + self.created
