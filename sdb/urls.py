from django.conf.urls import url
from sdb.views import *

app_name = 'sdb'

urlpatterns = [
    #API
    url(r'api/schema', api_schema),
    url(r'api/family/(?P<family>.+)', api_family),
    url(r'api/sequence/(?P<sequence_name>.+)', api_sequence),
    url(r'api', api_doc),

    url(r'^$', home_load),
    url(r'family/(?P<family>.+)', family_load, name="family"),
    url(r'sequence/(?P<sequence_name>.+)', sequence_load, name="sequence"),
    url(r'search/(?P<term>.+)', search),
    url(r'about', page_load, {'template_name': 'about.html'}),
    url(r'hmmsearch', page_load, {'template_name': 'hmmscan.html'}),
    url(r'results', hmm_results),


    url(r'feedback', page_load, {'template_name': 'feedback.html'}),

    #Internal Ajax
    url(r'ajax/proteins/(?P<pfam_acc>.+)', protein_table, name="ajax_proteins"),
    url(r'ajax/protvista_js/(?P<pfam_id>.+)', protvista_js, name="ajax_protvista_js"),
    url(r'ajax/hmmer', hmmer, name="hmmer"),
]