"""wbhb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from wbhb.viewer import views as viewer_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.site.site_header = 'Beowulf Bibliography'
admin.site.site_title = 'Beowulf Bibliography'

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^$', viewer_views.index, name='home'),
    re_path(r'^detail$', viewer_views.source_detail, name='detail'),
    re_path(r'^export$', viewer_views.export, name='export'),
    re_path(r'^sources$', viewer_views.sources, name='sources'),
    re_path(r'^people$', viewer_views.people, name='people'),
    re_path(r'^roles$', viewer_views.roles, name='roles'),
    re_path(r'^locations$', viewer_views.locations, name='locations'),
    re_path(r'^languages$', viewer_views.languages, name='languages'),
    re_path(r'^publishers$', viewer_views.publishers, name='publishers'),
    re_path(r'^fields$', viewer_views.fields, name='fields'),
    re_path(r'^periods$', viewer_views.periods, name='periods'),
    re_path(r'^graph$', viewer_views.relationship_graph, name='graph'),
    path('page/<str:slug>', viewer_views.page),
]

urlpatterns += staticfiles_urlpatterns()
