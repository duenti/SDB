from django.shortcuts import render
from sdb.models import *
from sdb.util import getReferences, parseDisulfide, parseSites
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import pickle

# 'global' variable storing amount of objects per page
per_page = 25
FTP_DIR="/Users/neli/Dropbox/Pfam32/"


# Create your views here.
def page_load(request, template_name):
    context = {}
    context['sidebar'] = True
    return render(request,template_name, context=context)


def home_load(request):
    template_name = "index.html"
    context = {}
    context['sidebar'] = True


    #paginator
    context['pfam_list'] = Pfama.objects.all()
    paginator = Paginator(context['pfam_list'], per_page)
    page = 1
    if 'page' in request.GET:
        page = request.GET["page"]
    try:
        context['pfam_list'] = paginator.page(page)
    except PageNotAnInteger:
        context['pfam_list'] = paginator.page(1)
    except EmptyPage:
        context['pfam_list'] = paginator.page(paginator.num_pages)


    return render(request, template_name, context=context)


def family_load(request,family):
    context = {}
    pfam = Pfama.objects.get(pk=family)
    pfam_id = pfam.pfama_id
    wiki_title = ""

    #Load MSA
    msa_dir = FTP_DIR + pfam.pfama_acc + "/msa.dic"
    with open(msa_dir, 'rb') as config_dictionary_file:
        msa = pickle.load(config_dictionary_file)
    print(len(msa))

    #Wikipedia
    result = Wikipedia.objects.raw("SELECT wikipedia.auto_wiki,title FROM pfam_32_0.pfamA_wiki, pfam_32_0.wikipedia WHERE pfamA_acc=\"" + family + "\" AND pfamA_wiki.auto_wiki=wikipedia.auto_wiki")
    if len(result) > 0:
        wiki_title = result[0].title

    #Communities (TEMP)
    context['communities'] = ["L46, A47, W291, L235, G282, Q126, I127, A85, L50, W78, C196, G123, C252, C314, C44, W135, S89, E88, C138, C223, F125, S115, C83, T93","G268, H260, E259, R262","A253, C328, W309","D248, D249","S72, G68"]

    #Disulfide Bonds
    bonds = parseDisulfide(pfam_id,msa)

    #Sites
    sites = parseSites(pfam_id,msa)
    print(sites)


    #References
    context['references'] = getReferences(pfam_id)
    print(context['references'])

    context['family'] = pfam #Usar pfam_id nas consultas
    context['wiki_title'] = wiki_title
    return render(request, template_name="family.html", context=context)

# def family_load(request, family):
#     context = {}
#     conf = Conformation.objects.all()[0]
#     pfam = Family.objects.get(pk=family)
#
#     #Only if not selected
#     min_score = pfam.conformation_set.aggregate(Min('score'))['score__min']
#     current_conformation = pfam.conformation_set.get(score=min_score)
#
#     context['family'] = pfam
#     context['conformation'] = current_conformation
#     context['prot_vist_src'] = generate_protvista_js(conf)
#     context['msa'] = getFasta(pfam)
#     context['sidebar'] = False
#
#     return render(request, template_name="family.html", context=context)