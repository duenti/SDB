from django.shortcuts import render
from sdb.models import *
from sdb.util import generate_protvista_js, getFasta

# Create your views here.
def page_load(request, template_name):
    return render(request,template_name)

def family_load(request, family):
    context = {}
    conf = Conformation.objects.all()[0]
    pfam = Family.objects.get(pk=family)

    context['family'] = pfam
    context['prot_vist_src'] = generate_protvista_js(conf)
    context['msa'] = getFasta(pfam)

    return render(request, template_name="family.html", context=context)