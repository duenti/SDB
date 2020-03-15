from sdb.models import *
from django.core.management.base import BaseCommand

RESULTS_PATH = '/Users/neli/Dropbox/Pfam32/'

def loadSequences(file, family_obj):
    fr = open(file)

    for line in fr:
        line = line.strip().split()
        if len(line) > 1:
            seqname = line[0]
            sequence = line[1]
            offset_str = seqname.split('/')[1].split('-')
            accession = seqname.split('/')[0]
            offset_from = int(offset_str[0])
            offset_to = int(offset_str[1])

            if Sequence.objects.filter(accession=accession).exists():
                seq_obj = Sequence.objects.get(accession=accession)
            else:
                seq_obj = Sequence(accession=accession)
                seq_obj.save()

            offset_obj = Offset(pos_from=offset_from,pos_to=offset_to,sequence=sequence,sequence_fk=seq_obj)
            offset_obj.save()
            family_obj.sequences.add(offset_obj)

    fr.close()

def parseCutoff(results_dir):
    temp_list = []
    final_list = []

    fr = open(results_dir + "cutoff.txt")

    for line in fr:
        temp = line.split()
        i = int(temp[0])
        pv = float(temp[2])
        temp_list.append((i,pv))

    fr.close()

    temp_list = sorted(temp_list, key=lambda tup: tup[1])

    cut = 0.6
    for i in range(len(temp_list)):
        i,pv = temp_list[i]
        if pv >= cut:
            while pv > cut:
                cut += 0.05
            final_list.append((i, pv, cut-0.05))

    return final_list

def getNetworkText(results_dir,residues,i):
    network = ""
    print(residues)
    fr = open(results_dir + "backbones/" + str(i))

    for line in fr:
        temp = line.split()
        if len(temp) > 1:
            ni = temp[0]
            nj = temp[1]
            if ni in residues and nj in residues:
                network += line

    fr.close()

    return network

def saveCommunities(results_dir, pfam_obj):
    cuts = parseCutoff(results_dir)

    for i, pv, cut in cuts:
        residues_set = set()
        fr = open(results_dir + "communities/" + str(i))
        conf_obj = Conformation(score=cut, family=pfam_obj)
        conf_obj.save()

        for line in fr:
            residues = line.strip()
            residues_set = residues_set.union(set(residues.split()))
            comm_obj = Community(residues=residues, score=pv, conformation=conf_obj, size=0)
            comm_obj.save()

        fr.close()

        network = getNetworkText(results_dir, residues_set, i)
        conf_obj.network = network
        conf_obj.save()

def load(pfam_id):
    working_dir = RESULTS_PATH + pfam_id

    pfam = Family(pfam_id=pfam_id)
    pfam.save()

    loadSequences(working_dir + "/msa.txt", pfam)
    results_dir = working_dir + "/results/"
    saveCommunities(results_dir, pfam)

    #ADD LOGGER

class Command(BaseCommand):
    def handle(self, **options):
        load("PF00062")
