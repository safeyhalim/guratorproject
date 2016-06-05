import StringIO
from PIL import Image
from django import forms
from django.forms import ModelForm, PasswordInput, CharField, ImageField, BooleanField, ChoiceField
from django.forms.widgets import SelectDateWidget
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from guratorapp.models import Participant, UserSurvey, RestaurantSurvey, GroupRestaurantSurvey
from django_countries import countries


class AuthForm(forms.Form):
    username = CharField(label="Username")
    password = CharField(widget=PasswordInput(), label="Password")
    
class PreferenceForm(forms.Form):
    password_new1 = CharField(widget=PasswordInput(), label="New password", required=False)
    password_new2 = CharField(widget=PasswordInput(), label="New password (confirmation)", required=False)
    password_old = CharField(widget=PasswordInput(), label="Current password", required=False)
    email = CharField(label="E-Mail address", required=False)
    country = ChoiceField(list(countries), label="Country", required=False)
    picture = ImageField(required=False)
    delete_picture = BooleanField(label="Delete profile photo", required=False)

    gps_long = CharField(required=False)
    gps_lat = CharField(required=False)

    def clean(self):
        cleaned_data = super(PreferenceForm, self).clean()

        password_new1 = cleaned_data.get("password_new1")
        password_new2 = cleaned_data.get("password_new2")
        password_old = cleaned_data.get("password_old")
        email = cleaned_data.get("email")
        delete_picture = cleaned_data.get("delete_picture")
        long = cleaned_data.get("gps_long")
        lat = cleaned_data.get("gps_lat")

        if password_new1 != password_new2:
            self.add_error("password_new1", "New passwords do not match!")

        if password_new1 != None and password_old != None and len(password_new1) > 0 and len(password_old) == 0:
            self.add_error("password_old", "Please enter the current password to change it!")

        if email != None:
            try:
                validate_email(email)
            except ValidationError as e:
                self.add_error('email', "Please enter a valid e-mail address")


        try:
            z = float(long)
        except ValueError:
            self.add_error("gps_long", "Wrong format (long)")

        try:
            z = float(lat)
        except ValueError:
            self.add_error("gps_lat", "Wrong format (lat)")

        if self.cleaned_data.get('picture') != None:
            image_field = self.cleaned_data.get('picture')
            image_file = StringIO.StringIO(image_field.read())
            image = Image.open(image_file)
            w, h = image.size
            # max size 500px
            max_size = 200
            ratio = min(max_size / float(w), max_size / float(h))

            if ratio < 1:
                image = image.resize((int(w * ratio), int(h * ratio)), Image.ANTIALIAS)
                image_file = StringIO.StringIO()
                image.save(image_file, 'JPEG', quality=90)

                image_field.file = image_file
                
class ParticipantEntryForm(ModelForm):
    password = CharField(widget=PasswordInput(), label="Please choose a password")
    password2 = CharField(widget=PasswordInput(), label="Please confirm the password")
    matriculation_number = CharField(label="Matriculation Number", required=False)

    class Meta:
        model = Participant
        # fields = ['name', 'gender','email', 'email2', 'accepted_terms_conditions','picture']
        fields = ['name', 'country', 'birthdate', 'email', 'email2', 'gender', 'accepted_terms_conditions', 'picture', 'real_name', 'gps_lat', 'gps_long']
        widgets = {
            'birthdate': SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"), years=range(1930, 2016)),
        }

    def clean(self):
        cleaned_data = super(ParticipantEntryForm, self).clean()
        email = cleaned_data.get("email")
        email2 = cleaned_data.get("email2")
        accepted_terms_conditions = cleaned_data.get("accepted_terms_conditions")

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        real_name = cleaned_data.get("real_name")
        gps_lat = cleaned_data.get("gps_lat")
        gps_long = cleaned_data.get("gps_long")

        name = cleaned_data.get("name")
        country = cleaned_data.get("country")
        birthdate = cleaned_data.get("birthdate")

        # Matriculation Number is not mandatory
        # try:
            # int(matriculation_number) < 10000:
            # self.add_error("matriculation_number", "Please add your matriculation number")
        # except:
        #   self.add_error("matriculation_number", "Please add your matriculation number")
         
        if name != None and len(name) > 0:
            name_clean = ''.join(name.split())

            if name_clean != name:
                self.add_error("name", "Please do not use whitespace (space, tab, etc.) in your username")
            try:
                name.decode("ascii")
            except:
                self.add_error("name", "Please only use ASCII in your username (i.e. no umlauts or other non-standard letters)")
                
        if country == None:
            self.add_error("country", "Please enter your country")
            
        if birthdate == None:
            self.add_error("birthdate", "Please enter your birthdate")

        if email != None:
            try:
                validate_email(email)
            except ValidationError as e:
                self.add_error('email', "Please enter a valid e-mail address")

        if email2 != None:
            if email != email2:
                self.add_error('email', "The email addresses do not match")

        if not accepted_terms_conditions:
            self.add_error('accepted_terms_conditions', "Please accept the terms and conditions to proceed")

        if gps_lat != None:
            try:
                i = gps_lat.index(".")
            except:
                success = False
                self.add_error('gps_lat', "Please provide correct value for latitude in decimal format, e.g. 48.9174128")
        if gps_long != None:
            try:
                i = gps_long.index(".")
            except:
                success = False
                self.add_error('gps_long', "Please provide correct value for longitude in decimal format, e.g. 11.4079934")

        if real_name == None:
            self.add_error("real_name", "Please provide your real name")
        else:
            if len(real_name) < 3 or real_name.find(" ") == -1:
                self.add_error("real_name", "Please provide your real name")

        if password != None:
            if len(password) < 4:
                self.add_error('password', "Please choose a longer password")
        if password2 != None:
            if password != password2:
                self.add_error('password2', "Passwords do not match")

        if self.cleaned_data.get('picture') != None:
            image_field = self.cleaned_data.get('picture')
            image_file = StringIO.StringIO(image_field.read())
            image = Image.open(image_file)
            w, h = image.size
            # max size 500px
            max_size = 200
            ratio = min(max_size / float(w), max_size / float(h))

            if ratio < 1:
                image = image.resize((int(w * ratio), int(h * ratio)), Image.ANTIALIAS)
                image_file = StringIO.StringIO()
                image.save(image_file, 'JPEG', quality=90)

                image_field.file = image_file
                

class PersonalityQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        try: 
            personality_questions = kwargs.pop('personality_questions')
            super(PersonalityQuestionForm, self).__init__(*args, **kwargs)
            for question in personality_questions:
                self.fields[str(question.id)] = forms.ChoiceField(widget=forms.RadioSelect, choices=(('A', question.optionA), ('B', question.optionB)))
        except:
            super(PersonalityQuestionForm, self).__init__(*args, **kwargs)
            

class UserSurveyForm(ModelForm):
    class Meta:
        model = UserSurvey
        fields = ['social_capital', 'tie_strength', 'social_similarity', 'social_context_similarity', 'sympathy', 'social_hierarchy', 'domain_expertise']
            

class RestaurantSurveyForm(ModelForm):
    class Meta:
        model = RestaurantSurvey
        fields = ['price', 'taste', 'clumsiness', 'service', 'hippieness', 'location', 'social_overlap', 'other']
        
class GroupRestaurantSurveyForm(ModelForm):
    class Meta:
        model = GroupRestaurantSurvey
        fields = ['price', 'taste', 'clumsiness', 'service', 'hippieness', 'location', 'social_overlap', 'other']
            
            
            
            
            
            
