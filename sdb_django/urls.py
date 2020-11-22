"""sdb_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from sdb.views import *

urlpatterns = [
    #API
    url(r'api/schema', api_schema),
    url(r'api/family/(?P<family>.+)', api_family),
    url(r'api/sequence/(?P<sequence_name>.+)', api_sequence),
    url(r'api', api_doc),

    path('admin/', admin.site.urls),
    url(r'^$', home_load),
    url(r'family/(?P<family>.+)', family_load),
    url(r'sequence/(?P<sequence_name>.+)', sequence_load, name="sequence"),
    url(r'search/(?P<term>.+)', search),
    url(r'about', page_load, {'template_name': 'about.html'}),


    url(r'feedback', page_load, {'template_name': 'feedback.html'}),

    #Internal Ajax
    url(r'ajax/proteins/(?P<pfam_acc>.+)', protein_table, name="ajax_proteins"),
    url(r'ajax/protvista_js/(?P<pfam_id>.+)', protvista_js, name="ajax_protvista_js"),

]
