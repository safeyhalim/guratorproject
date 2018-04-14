"""guratorproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

#includes the used url pattern
from django.conf.urls import include, url
#automatic Django administrative interface
from django.contrib import admin
from guratorapp import views

urlpatterns = [
    # url(r'^guratorapp/', include('guratorapp.urls')),
    # url(r'^i_am_too_late/', views.start),
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login_user, name='login_user'),
    url(r'^logout/', views.logout_user, name='logout_user'),
    url(r'^start/', views.start, name='start'),
    url(r'^personality_test/', views.personality_test, name='personality_test'),
    url(r'^select_user/', views.select_user, name='select_user'),
    url(r'^user_survey/', views.user_survey, name='user_survey'),
    url(r'^create_group/', views.create_group, name='create_group'),
    url(r'^restaurant_survey/', views.restaurant_survey, name='restaurant_survey'),
    url(r'^group_restaurant_survey/', views.group_restaurant_survey, name='group_restaurant_survey'),
    url(r'^select_restaurant/', views.select_restaurant, name='select_restaurant'),
    url(r'^select_group_restaurant/', views.select_group_restaurant, name='select_group_restaurant'),
    url(r'^select_group/', views.select_group, name='select_group'),
    url(r'^home/', views.home),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^help/', views.help_view, name='help_view'),
    url(r'^check_register_input/', views.check_register_input),
    url(r'^admin/', admin.site.urls),
]
