from django.shortcuts import render, redirect
from django.http import HttpResponse
from sdb.util import *
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import pickle
from sdb_django.settings import FTP_DIR
from django.db.models import Q
import json

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

    context['sdb_n'] = Pfama.objects.filter(sdb=True).count()
    context['pfam_n'] = Pfama.objects.all().count()
    context['sdb_fraction'] = int((context['sdb_n']/context['pfam_n'])*100)


    #paginator
    context['pfam_list'] = Pfama.objects.filter(sdb=True)
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
    #pfam = Pfama.objects.get(pk=family)
    pfam = Pfama.objects.get(Q(pfama_acc=family)|Q(pfama_id=family))
    pfam_id = pfam.pfama_id
    pfam_acc = pfam.pfama_acc
    family = pfam_acc
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

    #References
    context['references'] = getReferences(pfam_id)

    context['family'] = pfam #Usar pfam_id nas consultas
    context['family_acc'] = pfam_acc
    context['family_id'] = pfam_id
    context['wiki_title'] = wiki_title
    return render(request, template_name="family.html", context=context)

def sequence_load(request,sequence_name):
    context = {}
    context['name'] = sequence_name
    #uniprot = Uniprot.objects.get(uniprot_acc=sequence_name)
    uniprot = Uniprot.objects.get(Q(uniprot_acc=sequence_name)|Q(uniprot_id=sequence_name))
    sequence_name = uniprot.uniprot_acc
    context['uniprot'] = uniprot

    if 'score' in request.GET:
        score = request.GET['score']
    else:
        score = 0.0

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

                fullseq_id = uniprot.uniprot_id + "/" + str(pos_start) + "-" + str(pos_end)
                align_seq = getAlignSequence(pfam_id, fullseq_id)
                if len(align_seq) > 0:
                    conformations = Conformation.objects.filter(pfam_id=pfam_id)
                    if len(conformations) > 0:
                        if conformations.filter(score__gte=score).count() > 0:
                            current_conformation = conformations.filter(score__gte=score).order_by("score")[0]
                        else:
                            current_conformation = conformations.all().order_by("score")[0]
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


def search(request,term):
    term = term.strip()
    if Pfama.objects.filter(Q(pfama_acc=term)|Q(pfama_id=term)).count() > 0:
        return redirect("family/" + term)
    elif Uniprot.objects.filter(Q(uniprot_acc=term)|Q(uniprot_id=term)).count() > 0:
        return redirect("sequence/" + term)
    return render(request, template_name="notfound.html")


#####API#####
def api_doc(request):
    context = {}
    context['sidebar'] = True
    return render(request, "api.html", context)

def api_schema(request):
    return render(request,'openapi_schema_local.json', content_type='application/json')

def api_family(request, family):
    result = {'pfam': {}}

    if Pfama.objects.filter(Q(pfama_acc=family) | Q(pfama_id=family)).count() > 0:
        pfam = Pfama.objects.get(Q(pfama_acc=family) | Q(pfama_id=family))
        pfam_id = pfam.pfama_id
        result['pfam']['id'] = pfam_id
        pfam_acc = pfam.pfama_acc
        result['pfam']['accession'] = pfam_acc
        result['pfam']['description'] = pfam.description
        result['pfam']['deposited'] = pfam.deposited_by
        result['pfam']['seed_source'] = pfam.seed_source
        result['pfam']['type'] = pfam.type
        result['pfam']['comment'] = pfam.comment
        result['pfam']['sequence_GA'] = pfam.sequence_ga
        result['pfam']['domain_GA'] = pfam.domain_ga
        result['pfam']['sequence_TC'] = pfam.sequence_tc
        result['pfam']['domain_TC'] = pfam.domain_tc
        result['pfam']['sequence_NC'] = pfam.sequence_nc
        result['pfam']['domain_NC'] = pfam.domain_nc
        result['pfam']['build_method'] = pfam.buildmethod
        result['pfam']['model_length'] = pfam.model_length
        result['pfam']['search_method'] = pfam.searchmethod
        result['pfam']['msv_lambda'] = pfam.msv_lambda
        result['pfam']['msv_mu'] = pfam.msv_mu
        result['pfam']['viterbi_lambda'] = pfam.viterbi_lambda
        result['pfam']['viterbi_mu'] = pfam.viterbi_mu
        result['pfam']['forward_lambda'] = pfam.forward_lambda
        result['pfam']['forward_tau'] = pfam.forward_tau
        result['pfam']['num_seed'] = pfam.num_seed
        result['pfam']['num_full'] = pfam.num_full
        result['pfam']['version'] = pfam.version
        result['pfam']['number_archs'] = pfam.number_archs
        result['pfam']['number_species'] = pfam.number_species
        result['pfam']['number_ncbi'] = pfam.number_ncbi
        result['pfam']['number_meta'] = pfam.number_meta
        result['pfam']['average_length'] = pfam.average_length
        result['pfam']['average_coverage'] = pfam.average_coverage
        result['pfam']['consensus'] = pfam.full_consensus
        result['pfam']['SDB'] = bool(pfam.sdb)
        family = pfam_acc

        if result['pfam']['SDB']:
            result['SDB'] = {}
            conformations = Conformation.objects.filter(pfam_id=family)
            if 'score' in request.GET:
                current_conformation = conformations.filter(score__gte=request.GET['score']).order_by("score")[0]
            else:
                try:
                    current_conformation = conformations.filter(score__gte=0.8).order_by("score")[0]
                except:
                    current_conformation = conformations.all().order_by("-score")[0]

            result['SDB']['score'] = current_conformation.score
            result['SDB']['num_residues'] = current_conformation.N
            result['SDB']['communities'] = {'msa_num': []}

            # Load MSA
            msa_dir = FTP_DIR + pfam.pfama_acc + "/msa.dic"
            with open(msa_dir, 'rb') as config_dictionary_file:
                msa = pickle.load(config_dictionary_file)

            for community in current_conformation.community_set.all():
                result['SDB']['communities']['msa_num'].append(community.get_residues())

                for seqname,sequence in msa.items():
                    offset = int(seqname.split('/')[1].split('-')[0])
                    seq_comm = alignCommunity2SeqCommunity(community.residues, sequence, offset)
                    if seqname in result['SDB']['communities']:
                        result['SDB']['communities'][seqname]['matches'].append(seq_comm[0].strip().split())
                        result['SDB']['communities'][seqname]['unmatches'].append(
                            seq_comm[1].strip().split())
                    else:
                        result['SDB']['communities'][seqname] = {'matches': [], 'unmatches': []}
                        result['SDB']['communities'][seqname]['matches'].append(seq_comm[0].strip().split())
                        result['SDB']['communities'][seqname]['unmatches'].append(
                            seq_comm[1].strip().split())


    json_string = json.dumps(result, sort_keys=True, indent=4)

    return HttpResponse(json_string, content_type="application/json")



def api_sequence(request, sequence_name):
    result = {'sequence': {}}

    if Uniprot.objects.filter(Q(uniprot_acc=sequence_name) | Q(uniprot_id=sequence_name)).count() > 0:
        uniprot = Uniprot.objects.get(Q(uniprot_acc=sequence_name) | Q(uniprot_id=sequence_name))
        result['sequence']['id'] = uniprot.uniprot_id
        result['sequence']['accession'] = uniprot.uniprot_acc
        result['sequence']['description'] = uniprot.description
        result['sequence']['evidence'] = Evidence.objects.get(evidence=uniprot.evidence).description
        result['sequence']['length'] = uniprot.length
        result['sequence']['species'] = uniprot.species
        result['sequence']['taxonomy'] = uniprot.taxonomy
        result['sequence']['ncbi_id'] = uniprot.ncbi_taxid
        result['sequence']['fragment'] = bool(uniprot.is_fragment)
        result['sequence']['sequence'] = uniprot.sequence.decode("utf-8")
        result['sequence']['reference_proteome'] = bool(uniprot.ref_proteome)
        result['sequence']['complete_proteome'] = bool(uniprot.complete_proteome)
        result['sequence']['ncbi_id'] = uniprot.ncbi_taxid


        #Disulfide bonds
        sql = disulfide_sequence_SQL.format(seqname=uniprot.uniprot_acc)
        disulfide_list = PfamseqDisulphide.objects.raw(sql)
        if len(disulfide_list) > 0:
            result['sequence']['disulfide'] = []
            for disulfide_reg in disulfide_list:
                result['sequence']['disulfide'].append({'start': disulfide_reg.bond_start, 'end': disulfide_reg.bond_end})

        #Sites
        sql = sites_sequence_SQL.format(seqname=uniprot.uniprot_acc)
        sites_list = PfamseqMarkup.objects.raw(sql)
        if len(sites_list) > 0:
            result['sequence']['sites'] = []
            for site_reg in sites_list:
                site = {
                    'position': site_reg.residue,
                    'annotation': site_reg.annotation,
                    'markup': auto_markup[site_reg.auto_markup]
                }
                result['sequence']['sites'].append(site)

        #Regions
        sql = region_sequence_SQL.format(seqname=uniprot.uniprot_acc)
        region_list = OtherReg.objects.raw(sql)
        if len(region_list) > 0:
            result['sequence']['regions'] = []
            for region_reg in region_list:
                site = {
                    'start': region_reg.seq_start,
                    'end': region_reg.seq_end,
                    'type': region_reg.type_id,
                    'source': region_reg.source_id
                }
                result['sequence']['regions'].append(site)

        #SDB

        #Get all families
        uniprots_sequence = UniprotRegFull.objects.filter(uniprot_acc=uniprot.uniprot_acc)
        pfam_acc_list = uniprots_sequence.values('pfama_acc').distinct()

        if pfam_acc_list.count() > 0:
            result['sequence']['families'] = []

            for pfam_dic in pfam_acc_list:
                result_pfam = {'pfam': {}}
                pfam_acc = pfam_dic['pfama_acc']
                pfam = Pfama.objects.get(pfama_acc=pfam_acc)

                result_pfam['pfam']['id'] = pfam.pfama_id
                result_pfam['pfam']['accession'] = pfam_acc
                result_pfam['pfam']['description'] = pfam.description

                uniprot_ranges = uniprots_sequence.filter(pfama_acc=pfam_acc).order_by("seq_start")
                if uniprot_ranges.count() > 0:
                    result_pfam['pfam']['subdomain'] = []

                    for uniprot_range in uniprot_ranges:
                        pos_start = uniprot_range.seq_start
                        pos_end = uniprot_range.seq_end
                        subdomain = {
                            'start': pos_start,
                            'end': pos_end
                        }
                        fullseq_id = uniprot.uniprot_id + "/" + str(pos_start) + "-" + str(pos_end)
                        align_seq = getAlignSequence(pfam_acc, fullseq_id)
                        if len(align_seq) > 0:
                            subdomain['aligned_sequence'] = align_seq

                            conformations = Conformation.objects.filter(pfam_id=pfam_acc)
                            if len(conformations) > 0:
                                if 'score' in request.GET:
                                    current_conformation = \
                                    conformations.filter(score__gte=request.GET['score']).order_by("score")[0]
                                else:
                                    try:
                                        current_conformation = conformations.filter(score__gte=0.8).order_by("score")[0]
                                    except:
                                        current_conformation = conformations.all().order_by("-score")[0]

                                subdomain['SDB'] = {}
                                subdomain['SDB']['score'] = current_conformation.score
                                subdomain['SDB']['num_residues'] = current_conformation.N

                                ams_communities = current_conformation.community_set.all()
                                if ams_communities.count() > 0:
                                    subdomain['SDB']['communities'] = []
                                    for community in ams_communities:
                                        matches, missmatches = alignCommunity2SeqCommunity(community.residues,
                                                                                           align_seq, pos_start)
                                        community_dic = {
                                            'msa_numbering': community.get_residues(),
                                            'seq_numbering': {
                                                'matches': matches,
                                                'unmatches': missmatches
                                            }
                                        }

                                        subdomain['SDB']['communities'].append(community_dic)

                        result_pfam['pfam']['subdomain'].append(subdomain)

                result['sequence']['families'].append(result_pfam)

    json_string = json.dumps(result, sort_keys=True, indent=4)

    return HttpResponse(json_string, content_type="application/json")

#########INTERNAL AJAX CALLS###########
def protein_table2(request, pfam_acc):
    table = []
    # Sequence table
    sql = '''
        SELECT pfamseq_acc,pfamseq_id,description FROM pfam_32_0.pfamseq
        WHERE pfamseq.pfamseq_acc IN (
        SELECT pfamseq_acc FROM pfamA_reg_full_significant WHERE pfamA_acc="{pfam_id}");
        '''.format(pfam_id=pfam_acc)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    context = {'table': result}

    return render(request, template_name="ajax/sequences_table.html", context=context)

def protein_table(request, pfam_acc):
    sequences = PfamaRegFullSignificant.objects.filter(pfama_acc="PF00062").values_list("pfamseq_acc","pfamseq_acc__pfamseq_id","pfamseq_acc__description")

    context = {'table': sequences}

    return render(request, template_name="ajax/sequences_table.html", context=context)

def protvista_js(request, pfam_id):
    pfam = Pfama.objects.get(pfama_id=pfam_id)
    pfam_acc = pfam.pfama_acc

    # Conformations
    conformations = Conformation.objects.filter(pfam_id=pfam_acc)

    if 'score' in request.GET:
        current_conformation = conformations.filter(score__gte=request.GET['score']).order_by("score")[0]
    else:
        try:
            current_conformation = conformations.filter(score__gte=0.8).order_by("score")[0]
        except:
            current_conformation = conformations.all().order_by("-score")[0]

    # Load MSA
    msa_dir = FTP_DIR + pfam.pfama_acc + "/msa.dic"
    with open(msa_dir, 'rb') as config_dictionary_file:
        msa = pickle.load(config_dictionary_file)

    # ProtVista
    context = {'prot_vist_src': generateProtVista(pfam, msa, current_conformation)}

    return render(request, template_name="ajax/protvista.html", context=context)

# Create your views here.
def test_page(request):
    context = {}
    context['sidebar'] = False
    return render(request,'test.html', context=context)