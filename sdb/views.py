from django.shortcuts import render
from sdb.models import *
from sdb.util import *
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import pickle
from sdb_django.settings import FTP_DIR

# 'global' variable storing amount of objects per page
per_page = 25



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
    pfam_acc = pfam.pfama_acc
    wiki_title = ""


    #Conformations
    conformations = Conformation.objects.filter(pfam_id=family)
    context['conformations'] = conformations

    if 'score' in request.GET:
        current_conformation = conformations.filter(score__gte=request.GET['score']).order_by("score")[0]
    else:
        try:
            current_conformation = conformations.filter(score__gte=0.8).order_by("score")[0]
        except:
            current_conformation = conformations.all().order_by("-score")[0]

    context['current_conformation'] = current_conformation

    #PDB image
    context['pdb'] = ""
    pdbs = PdbPfamaReg.objects.filter(pfama_acc=pfam.pfama_acc)
    if pdbs.count() > 0:
        context['pdb'] = pdbs[0].pdb_id

    #GOs
    sql = "SELECT *, go_id as id FROM gene_ontology WHERE pfamA_acc='{pfam_acc}' ORDER BY category;"
    context['gos'] = GeneOntology.objects.raw(sql.format(pfam_acc=pfam_acc))

    #INTERPRO
    sql = "SELECT *, interpro_id as id FROM interpro WHERE pfamA_acc='{pfam_acc}';"
    context['interpro'] = GeneOntology.objects.raw(sql.format(pfam_acc=pfam_acc))

    #Load MSA
    msa_dir = FTP_DIR + pfam.pfama_acc + "/msa.dic"
    with open(msa_dir, 'rb') as config_dictionary_file:
        msa = pickle.load(config_dictionary_file)

    #Load Network
    networkjs_dir = FTP_DIR + pfam.pfama_acc + "/results/networkjs/" + str(current_conformation.N) + ".ser" #TEMP
    with open(networkjs_dir, 'rb') as config_dictionary_file:
        context['networkjs'] = pickle.load(config_dictionary_file)

    # Load Matrix
    matrix_dir = FTP_DIR + pfam.pfama_acc + "/results/matrix/" + str(current_conformation.N) + ".ser"  # TEMP
    with open(matrix_dir, 'rb') as config_dictionary_file:
        context['matrix'] = pickle.load(config_dictionary_file)

    #Wikipedia
    result = Wikipedia.objects.raw("SELECT wikipedia.auto_wiki,title FROM pfam_32_0.pfamA_wiki, pfam_32_0.wikipedia WHERE pfamA_acc=\"" + family + "\" AND pfamA_wiki.auto_wiki=wikipedia.auto_wiki")
    if len(result) > 0:
        wiki_title = result[0].title

    #Communities
    context['communities'] = current_conformation.community_set.all()
    #context['communities'] = ["L46, A47, W291, L235, G282, Q126, I127, A85, L50, W78, C196, G123, C252, C314, C44, W135, S89, E88, C138, C223, F125, S115, C83, T93","G268, H260, E259, R262","A253, C328, W309","D248, D249","S72, G68"]

    #ProtVista
    context['prot_vist_src'] = generateProtVista(pfam,msa,current_conformation)


    #References
    context['references'] = getReferences(pfam_id)

    context['family'] = pfam #Usar pfam_id nas consultas
    context['wiki_title'] = wiki_title
    return render(request, template_name="family.html", context=context)

def sequence_load(request,sequence_name):
    context = {}
    context['name'] = sequence_name
    uniprot = Uniprot.objects.get(uniprot_acc=sequence_name)
    context['uniprot'] = uniprot

    #TEMP
    score = 0.6

    #Get all families
    pfam_communities = {}
    uniprots_sequence = UniprotRegFull.objects.filter(uniprot_acc=sequence_name)
    pfam_acc_list = uniprots_sequence.values('pfama_acc').distinct()
    context['pfam_acc_list'] = pfam_acc_list
    for pfam_dic in pfam_acc_list:
        pfam_id = pfam_dic['pfama_acc']
        #print("###" + pfam_id + "###")

        uniprot_ranges = uniprots_sequence.filter(pfama_acc=pfam_id).order_by("seq_start")
        if uniprot_ranges.count() > 0:
            pfam_communities[pfam_id] = []

            for uniprot_range in uniprot_ranges:
                pos_start = uniprot_range.seq_start
                pos_end = uniprot_range.seq_end
                interval_str = str(pos_start) + " - " + str(pos_end)
                #print(interval_str)

                fullseq_id = uniprot.uniprot_id + "/" + str(pos_start) + "-" + str(pos_end)
                align_seq = getAlignSequence(pfam_id, fullseq_id)
                if len(align_seq) > 0:
                    conformations = Conformation.objects.filter(pfam_id=pfam_id)
                    if len(conformations) > 0:
                        current_conformation = conformations.all()[0]  # TEMP
                        ams_communities = current_conformation.community_set.all()
                        if ams_communities.count() > 0:
                            interval_comm = []
                            for community in ams_communities:
                                matches, missmatches = alignCommunity2SeqCommunity(community.residues, align_seq, pos_start)
                                comm_str = "<span style='color:darkgreen;'>" + matches + "</span>"
                                if len(missmatches) > 0:
                                    comm_str += " <span style='color:red;'>[ " + missmatches + "]</span>"
                                interval_comm.append(comm_str)

                            pfam_communities[pfam_id].append((interval_str,interval_comm))
    context['pfam_communities'] = pfam_communities

        # conformations = Conformation.objects.filter(pfam_id=pfam_id)
        # if len(conformations) > 0:
        #     print("###" + pfam_id + "###")
        #     current_conformation = conformations.all()[0]#TEMP
        #     ams_communities = current_conformation.community_set.all()
        #     for community in ams_communities:
        #         print(community.residues)



    # ProtVista
    context['prot_vist_src'] = generateProtVistaSequence(sequence_name)


    return render(request, template_name="sequence.html", context=context)