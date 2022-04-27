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
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from wbhb.viewer import views as viewer_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.site.site_header = 'Beowulf Bibliography'
admin.site.site_title = 'Beowulf Bibliography'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', viewer_views.index, name='home'),
    url(r'^detail$', viewer_views.source_detail, name='detail'),
    url(r'^export$', viewer_views.export, name='export'),
    url(r'^sources$', viewer_views.sources, name='sources'),
    url(r'^people$', viewer_views.people, name='people'),
    url(r'^roles$', viewer_views.roles, name='roles'),
    url(r'^locations$', viewer_views.locations, name='locations'),
    url(r'^languages$', viewer_views.languages, name='languages'),
    url(r'^publishers$', viewer_views.publishers, name='publishers'),
    url(r'^fields$', viewer_views.fields, name='fields'),
    url(r'^periods$', viewer_views.periods, name='periods'),
    url(r'^graph$', viewer_views.relationship_graph, name='graph'),
    path('page/<str:slug>', viewer_views.page),
]

urlpatterns += staticfiles_urlpatterns()
