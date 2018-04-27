# coding=utf-8
# Combines a given template with a given context dictionary and returns an HttpResponse object with that rendered text.
from django.shortcuts import render
from guratorapp.forms import ParticipantEntryForm, PreferenceForm, AuthForm, \
    PersonalityQuestionForm, UserSurveyForm, RestaurantSurveyForm, GroupRestaurantSurveyForm
from guratorapp.models import Participant, PersonalityQuestion, \
    ParticipantPersonalityQuestion, UserSurvey, RestaurantSurvey, Group, GroupParticipant, GroupRestaurantSurvey
# enables the creation of users
from django.contrib.auth.models import User
# Keyword argument queries are "and"ed together. If you need to execute more complex queries like "or" you can use Q objects.
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings as conf_settings
import json

############################### Constants #####################################
NUM_SURVEY = 10
NUM_RESTAURANT_SURVEY = 1
MAX_NUM_IN_GROUP = 10000  # Setting a very large number: effectively: a participant can add any number of participants in his group
MIN_NUM_IN_GROUP = 0
NUM_GROUPS_FOR_PARTICIPANT = 10000  # Setting a very large number: effectively: a participant can be in any number of groups


#   --------------------------- Utility functions ------------------------------ #
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_surveyed_participants(participant):
    already_surveyed_participant_ids = UserSurvey.objects.filter(from_participant=participant).values_list('to_participant', flat=True)
    num_remaining = NUM_SURVEY - already_surveyed_participant_ids.count()  # Number of participants that the current participant still needs to do survey for
    return already_surveyed_participant_ids, num_remaining


def get_participants_in_the_same_groups(participant):
    group_ids = GroupParticipant.objects.filter(participant=participant).values_list('group', flat=True)
    participant_ids = GroupParticipant.objects.filter(group__in=group_ids).values_list('participant', flat=True).distinct()
    return participant_ids


def get_participant_ids_assigned_to_max_num_groups():
    participant_ids = Participant.objects.all().values_list('id', flat=True)
    excluded_ids = []
    for participant_id in participant_ids:
        num_groups = GroupParticipant.objects.filter(participant=participant_id).count()
        if num_groups < NUM_GROUPS_FOR_PARTICIPANT:
            excluded_ids.append(participant_id)
    pids = participant_ids.exclude(Q(id__in=excluded_ids))
    return pids


def get_current_menu_info(request):
    personality_test_done = False
    user_survey_almost_done = False  # Relevant to ProductionPhase3
    user_survey_done = False 
    restaurant_survey_done = False
    # group_creation_done = False
    group_restaurant_survey_done = True
    if request.user.is_authenticated():
        if request.user.participant.personality_test_done == True:
            personality_test_done = True
            _, num_remaining = get_surveyed_participants(request.user.participant)
            if num_remaining <= 16:  # NOTE: this is applicable only for ProductionPhase3, the students can start rating restaurants if they already have surveyed 24 participants (20 externals and 4 internals)
                user_survey_almost_done = True
                if num_remaining == 0:
                    user_survey_done = True
                restaurants = parse_restaurants_json()
                _, num_restaurants_remaining = get_restaurants(restaurants, request.user.participant)
                if num_restaurants_remaining == 0:
                    restaurant_survey_done = True
                    # groups = GroupParticipant.objects.filter(participant=request.user.participant).values_list('group', flat=True)
                    # num_groups = groups.count()
                    # if num_groups == NUM_GROUPS_FOR_PARTICIPANT:
                        # group_creation_done = True
                        # for group in groups:
                            # _, num_remaining_group_restaurants = get_group_restaurants(restaurants, group)
                            # if num_remaining_group_restaurants > 0:
                                # group_restaurant_survey_done = False
                                # break
                                
    # return {"personality_test_done": personality_test_done, "user_survey_almost_done": user_survey_almost_done, "user_survey_done": user_survey_done, "restaurant_survey_done": restaurant_survey_done, "group_creation_done": group_creation_done, "group_restaurant_survey_done": group_restaurant_survey_done}
    return {"personality_test_done": personality_test_done, "user_survey_almost_done": user_survey_almost_done, "user_survey_done": user_survey_done, "restaurant_survey_done": restaurant_survey_done, "group_restaurant_survey_done": group_restaurant_survey_done}
    

def parse_restaurants_json():
    # path = "/Users/shalim/liclipse_workspace/guratorproject/yelp.json"
    path = conf_settings.YELP_RESTAURANT_PATH
    with open(path) as restaurants_file:  
        restaurants_dict = json.loads(restaurants_file.read())
    return restaurants_dict["restaurants"]  # returns a list of dictionaries, each of which represents a restaurant


def get_restaurant_by_id(restaurants, target_restaurant_id):
    for restaurant in restaurants:
        if restaurant["id"] == target_restaurant_id:
            return restaurant
    return None


# all restaurants without the already surveyed
def get_restaurants(all_restaurants, current_participant):
    surveyed_restaurant_ids = RestaurantSurvey.objects.filter(participant=current_participant).values_list('restaurant_id', flat=True)
    for restaurant in all_restaurants:
        if restaurant["id"] in surveyed_restaurant_ids:
            all_restaurants.remove(restaurant)
    return all_restaurants, NUM_RESTAURANT_SURVEY - surveyed_restaurant_ids.count()


# all restaurants without the already surveyed
def get_group_restaurants(all_restaurants, current_group):
    surveyed_restaurant_ids = GroupRestaurantSurvey.objects.filter(group=current_group).values_list('restaurant_id', flat=True)
    for restaurant in all_restaurants:
        if restaurant["id"] in surveyed_restaurant_ids:
            all_restaurants.remove(restaurant)
    return all_restaurants, NUM_RESTAURANT_SURVEY - surveyed_restaurant_ids.count()    
        

# --------------------------- End of Utility functions --------------------------------------- #

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    return render(request, 'guratorapp/index.html')


def help_view(request):
    return render(request, 'guratorapp/help.html', {"menu": get_current_menu_info(request)})


@login_required
def home(request):
    p = Participant.objects.get(user=request.user)
    return render(request, 'guratorapp/home.html', {"user": request.user, "participant": p,
                                                    "menu": get_current_menu_info(request),
                                                    })


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def login_user(request):
    if request.method == "POST":
        form = AuthForm(request.POST)
        if form.is_valid():
            username = request.POST['username'].lower()
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/home/")
                else:
                    # Return a 'disabled account' error message
                    form.add_error("username", "Account has been disabled.")
            else:
                # Return an 'invalid login' error message.
                form.add_error("username", "Username and password do not match.")
    else:
        form = AuthForm()
    return render(request, 'guratorapp/login.html', {"form": form})


@login_required
def restaurant_survey(request):
    if request.method == "POST":
        form = RestaurantSurveyForm(request.POST)
        target_restaurant_id = request.POST.get("restaurant_id",)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            restaurant_survey = RestaurantSurvey()
            restaurant_survey.participant = request.user.participant
            restaurant_survey.restaurant_yelp_id = target_restaurant_id
            restaurant_survey.price = cleaned_data["price"]
            restaurant_survey.taste = cleaned_data["taste"]
            restaurant_survey.clumsiness = cleaned_data["clumsiness"]
            restaurant_survey.service = cleaned_data["service"]
            restaurant_survey.hippieness = cleaned_data["hippieness"]
            restaurant_survey.location = cleaned_data["location"]
            restaurant_survey.social_overlap = cleaned_data["social_overlap"]
            restaurant_survey.other = cleaned_data["other"]
            restaurant_survey.save()

            restaurant_survey_count = RestaurantSurvey.objects.filter(participant=request.user.participant).count()
            if restaurant_survey_count == NUM_RESTAURANT_SURVEY:
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponseRedirect('/select_restaurant/')
    else:  # GET request
        target_restaurant_id = request.GET.get("t", "")
    form = RestaurantSurveyForm()
    return render(request, 'guratorapp/restaurant_survey.html', {"user": request.user, "form": form, "restaurant_id": target_restaurant_id, "menu": get_current_menu_info(request)})


@login_required
def group_restaurant_survey(request):
    if request.method == "POST":
        form = GroupRestaurantSurveyForm(request.POST)
        group_id = request.POST.get("group_id", "")
        target_restaurant_id = request.POST.get("restaurant_id", "")
        group = Group.objects.get(id=group_id)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            group_restaurant_survey = GroupRestaurantSurvey()
            group_restaurant_survey.group = group
            group_restaurant_survey.restaurant_yelp_id = target_restaurant_id
            group_restaurant_survey.price = cleaned_data["price"]
            group_restaurant_survey.taste = cleaned_data["taste"]
            group_restaurant_survey.clumsiness = cleaned_data["clumsiness"]
            group_restaurant_survey.service = cleaned_data["service"]
            group_restaurant_survey.hippieness = cleaned_data["hippieness"]
            group_restaurant_survey.location = cleaned_data["location"]
            group_restaurant_survey.social_overlap = cleaned_data["social_overlap"]
            group_restaurant_survey.other = cleaned_data["other"]
            group_restaurant_survey.save()

            group_restaurant_survey_count = GroupRestaurantSurvey.objects.filter(group=group).count()
            if group_restaurant_survey_count == NUM_RESTAURANT_SURVEY:
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponseRedirect('/select_group_restaurant/?g=' + str(group.id))
    else:
        group_id = request.GET.get("g", "")
        target_restaurant_id = request.GET.get("t", "")
    group = Group.objects.get(id=group_id)
    form = GroupRestaurantSurveyForm()
    return render(request, 'guratorapp/group_restaurant_survey.html', {"user": request.user, "form": form, "restaurant_id": target_restaurant_id, "group": group, "menu": get_current_menu_info(request)})
    

@login_required
def select_group_restaurant(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        target_restaurant_id = request.POST.get("submitBtn")
        return HttpResponseRedirect('/group_restaurant_survey/?t=' + target_restaurant_id + '&g=' + group_id)
    else:  # GET request
        group_id = request.GET.get("g", "")
    
    group = Group.objects.get(id=group_id)
    # all_restaurants = parse_restaurants_json()
    # restaurants, num_remaining_restaurants = get_group_restaurants(all_restaurants, group)
    surveyed_count = GroupRestaurantSurvey.objects.filter(group=group).count()
    num_remaining_restaurants = NUM_RESTAURANT_SURVEY - surveyed_count
    return render(request, 'guratorapp/select_group_restaurant.html', {"user": request.user, "group": group, "num_remaining_restaurants": num_remaining_restaurants, "menu": get_current_menu_info(request)})


@login_required
def select_restaurant(request):
    # all_restaurants = parse_restaurants_json()
    # restaurants, num_remaining_restaurants = get_restaurants(all_restaurants, request.user.participant)
    survey_count = RestaurantSurvey.objects.filter(participant=request.user.participant).count()
    num_remaining_restaurants = NUM_RESTAURANT_SURVEY - survey_count
    if request.method == "POST":
        target_restaurant_id = request.POST.get("submitBtn")
        if target_restaurant_id is None:
            return HttpResponseRedirect('/home/')
        return HttpResponseRedirect('/restaurant_survey/?t=' + target_restaurant_id)
    return render(request, 'guratorapp/select_restaurant.html', {"user": request.user, "num_remaining_restaurants": num_remaining_restaurants, "menu": get_current_menu_info(request)})


@login_required
def user_survey(request):
    if request.method == "POST":
        form = UserSurveyForm(request.POST)
        target_participant_id = request.POST.get("target_participant_id",)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user_survey = UserSurvey()
            user_survey.from_participant = request.user.participant
            user_survey.to_participant = Participant.objects.get(id=target_participant_id)
            user_survey.relationship = cleaned_data["relationship"]
            user_survey.social_capital = cleaned_data["social_capital"]
            user_survey.tie_strength = cleaned_data["tie_strength"]
            user_survey.social_similarity = cleaned_data["social_similarity"]
            user_survey.social_context_similarity = cleaned_data["social_context_similarity"]
            user_survey.sympathy = cleaned_data["sympathy"]
            user_survey.social_hierarchy = cleaned_data["social_hierarchy"]
            user_survey.domain_expertise = cleaned_data["domain_expertise"]
            user_survey.save()
            
            survey_count = UserSurvey.objects.filter(from_participant=request.user.participant).count()
            if survey_count == NUM_SURVEY:
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponseRedirect('/select_user/')
                                     
    else:  # GET request
        target_participant_id = request.GET.get("t", "") 
        
    target_participant = Participant.objects.get(id=target_participant_id)
    form = UserSurveyForm()
    return render(request, 'guratorapp/user_survey.html', {"user": request.user, "form": form, "target_participant": target_participant, "menu": get_current_menu_info(request)})


@login_required
def select_group(request):
    participant = request.user.participant
    participant_groups = participant.groups.all()
    # Remove groups that already have been surveyed
    all_restaurants = parse_restaurants_json()
    remaining_groups = []
    for group in participant_groups:
        _, num_remaining_group_restaurants = get_group_restaurants(all_restaurants, group)
        if num_remaining_group_restaurants > 0:
            remaining_groups.append(group)
            
    if request.method == "POST":
        group_id = request.POST.get("submitBtn", "")
        return HttpResponseRedirect('/select_group_restaurant/?g=' + group_id)
    return render(request, 'guratorapp/select_group.html', {"user": request.user, "groups": remaining_groups, "menu": get_current_menu_info(request)})


@login_required
def select_user(request):
    participant = request.user.participant
    already_surveyed_participant_ids, num_remaining = get_surveyed_participants(participant)
    target_participants = Participant.objects.exclude(Q(id__in=already_surveyed_participant_ids) | Q(id=participant.id))  # select all participants except the current user and all the participants already surveyed
    if request.method == "POST":
        target_participant_id = request.POST.get("submitBtn", "")
        return HttpResponseRedirect('/user_survey/?t=' + target_participant_id)
    return render(request, 'guratorapp/select_user.html', {"user": request.user, "target_participants": target_participants, "num_remaining": num_remaining, "menu": get_current_menu_info(request)})


@login_required
def create_group(request):
    participant = request.user.participant
    if request.method == "POST":
        group_name = request.POST.get("group_name",)
        group = Group()
        group.name = group_name
        group.creator = participant
        group.save()
        group_participant = GroupParticipant()  # Group creator is also a group participant
        group_participant.participant = participant
        group_participant.group = group
        group_participant.save()
        for name, _ in request.POST.items():
            if name.startswith("participant_"):
                participant_id = name.split("participant_")[1]
                member_participant = Participant.objects.get(id=participant_id)
                group_participant = GroupParticipant()
                group_participant.group = group
                group_participant.participant = member_participant
                group_participant.save()
        num_groups = GroupParticipant.objects.filter(participant=participant).count()
        if num_groups == NUM_GROUPS_FOR_PARTICIPANT:
            return HttpResponseRedirect('/home/')
    else:  # GET request
        num_groups = GroupParticipant.objects.filter(participant=participant).count()
    num_remaining = NUM_GROUPS_FOR_PARTICIPANT - num_groups
    participant_ids_in_same_groups = get_participants_in_the_same_groups(participant)  # Show participants and exclude the current participant and those already members in the same groups as the current participant
    # surveyed_participant_ids = UserSurvey.objects.filter(from_participant=participant).values_list('to_participant')
    # surveyed_participants = Participant.objects.filter(Q(id__in=surveyed_participant_ids))
    participants_in_max_num_groups = get_participant_ids_assigned_to_max_num_groups() 
    target_participants = Participant.objects.exclude(Q(id=participant.id) | Q(id__in=participant_ids_in_same_groups) | Q(id__in=participants_in_max_num_groups))  # Relaxing the conditions: making it possible to add participants to the group even if you didn't survey them
    # target_participants = surveyed_participants.exclude(Q(id__in=participant_ids_in_same_groups) | Q(id__id=participants_in_max_num_groups))
    return render(request, 'guratorapp/create_group.html', {"user": request.user, "target_participants": target_participants, "min_participants_in_group": MIN_NUM_IN_GROUP, "max_participants_in_group": MAX_NUM_IN_GROUP, "num_remaining": num_remaining, "menu": get_current_menu_info(request)})


@login_required
def personality_test(request):
    if request.method == "POST":
        personality_questions = PersonalityQuestion.objects.all()
        form = PersonalityQuestionForm(request.POST, personality_questions=personality_questions)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            participant = request.user.participant
            for _id, answer in cleaned_data.items():
                ppq = ParticipantPersonalityQuestion(participant=participant, personality_question=personality_questions.get(id=int(_id)), answer=answer)
                ppq.save()
            participant.personality_test_done = True
            participant.save()
            return HttpResponseRedirect('/home/')

    else:  # GET
        questions = PersonalityQuestion.objects.all()
        form = PersonalityQuestionForm(personality_questions=questions)
    return render(request, 'guratorapp/personality_test.html', {"user": request.user, "form": form, "menu": get_current_menu_info(request)})


@login_required
def settings(request):
    if request.method == "POST":
        form = PreferenceForm(request.POST, request.FILES)
        if form.is_valid():

            # check ob altes Passwort stimmt
                password_old = form.cleaned_data["password_old"]
                password_new = form.cleaned_data["password_new1"]
                email = form.cleaned_data["email"]
                country = form.cleaned_data["country"]
                delete_picture = form.cleaned_data["delete_picture"]

                _long = form.cleaned_data["gps_long"]
                lat = form.cleaned_data["gps_lat"]


                if request.user.check_password(password_old):
                    if len(password_new) > 0:
                        request.user.set_password(password_new)
                        request.user.save()
                        # gleich wieder neu einloggen
                        update_session_auth_hash(request, request.user)
                        # user = authenticate(username=request.user.username, password=password_new)

                    if len(email) > 0:
                        request.user.participant.email = email
                        request.user.participant.save()
                    if delete_picture:
                        request.user.participant.picture = ""
                        request.user.participant.save()
                    # save the great pic
                    if form.cleaned_data['picture'] is not None:
                        request.user.participant.picture = form.cleaned_data['picture']
                        request.user.participant.save()



                    request.user.participant.gps_long = _long
                    request.user.participant.gps_lat = lat
                    request.user.participant.country = country
                    request.user.participant.save()

                    return HttpResponseRedirect('/home/')
                else:
                    form.add_error("password_old", "Please enter your current password to make changes.")
    else:
        form = PreferenceForm(initial={'email':request.user.participant.email, 'country':request.user.participant.country, 'gps_long':request.user.participant.gps_long, 'gps_lat':request.user.participant.gps_lat})
    return render(request, 'guratorapp/settings.html', {"form":form
                                                        , "menu":get_current_menu_info(request)
                                                        })


def start(request):
    """
    Session ID is fixed, participant id is done

    Required steps:
    - n/a
    """
    if request.method == "POST":
        form = ParticipantEntryForm(request.POST, request.FILES)
        if form.is_valid():
            success = True
            try:
                user = User.objects.create_user(form.cleaned_data["name"].lower(), form.cleaned_data["email"].lower(), form.cleaned_data["password"])
                user.save()
            except:
                form.add_error('name', "Username already taken - please chose a different one (and only register once)")
                success = False

            if success:
                p = Participant(name="", user=user, email=" ", email2=" ", ip=get_client_ip(request))
                p.name = form.cleaned_data["name"].lower()
                p.gender = form.cleaned_data['gender'].lower()
                p.country = form.cleaned_data['country']
                p.birthdate = form.cleaned_data['birthdate']
                p.email = form.cleaned_data['email'].lower()
                p.email2 = form.cleaned_data['email2'].lower()
                p.accepted_terms_conditions = form.cleaned_data['accepted_terms_conditions']
                p.picture = form.cleaned_data['picture']
                p.real_name = form.cleaned_data["real_name"]
                p.gps_lat = form.cleaned_data["gps_lat"]
                p.gps_long = form.cleaned_data["gps_long"]
                if form.cleaned_data["matriculation_number"] is not None:
                    p.matriculation_number = form.cleaned_data["matriculation_number"]
                p.save()

                u = authenticate(username=user.username, password=form.cleaned_data["password"])

                if u is not None:
                    if u.is_active:
                        login(request, u)
                return HttpResponseRedirect("/home/")
    else:
        form = ParticipantEntryForm()

    return render(request, 'guratorapp/participant.html', {"user":request.user, "form":form})


# Handles Ajax call
def check_register_input(request):
    if request.method == "POST":
        elem_id = request.POST["elem_id"]
        value = request.POST["value"]
        resp = {"success":False}
        if elem_id == "id_name":
            z = Participant.objects.filter(name=value).count()
            if z == 0:
                resp = {"success":True}
        return JsonResponse(resp)
    else:
        return render(request, 'guratorapp/basic_message.html',
                      {"title": "Forbidden", "message": "You are not allowed to access this content."
                        , "menu": get_current_menu_info(request),
                        })


def image_connector(request):
    from guratorapp.templatetags import extras

    p = request.GET['p']
    username = p[p.index("(") + 1:p.index(")")]

    try:
        u = Participant.objects.filter(name=username)
    except:
        u = []
    if len(u) > 0:
        x = u[0]
        # print u[0].picture.name
        return HttpResponse(extras.get_image_path(x.picture.name))
    else:
        return HttpResponse(HttpResponse(extras.get_image_path("")))
