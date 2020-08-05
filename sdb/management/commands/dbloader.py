from sdb.models import *
from django.core.management.base import BaseCommand
from glob import glob
import os
from os import path

RESULTS_PATH = "/Volumes/Fast SSD/Pfam32/"

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

    cut = 0.7
    for i in range(len(temp_list)):
        i,pv = temp_list[i]
        if pv >= cut:
            while pv > cut:
                cut += 0.05
            final_list.append((i, pv, cut-0.05))

    return final_list

def saveCommunities(results_dir, pfam_id):
    cuts = parseCutoff(results_dir)

    for i, pv, cut in cuts:
        residues_set = set()
        fr = open(results_dir + "communities/" + str(i))
        conf_obj = Conformation(pfam_id=pfam_id, score=cut, N=i)
        conf_obj.save()

        for line in fr:
            residues = line.strip()
            residues_set = residues_set.union(set(residues.split()))
            comm_obj = Community(residues=residues, conformation=conf_obj)
            comm_obj.save()

        fr.close()

def load(pfam_id):
    print(pfam_id)
    working_dir = RESULTS_PATH + pfam_id

    results_dir = working_dir + "/results/"
    if os.path.exists(results_dir):
        saveCommunities(results_dir, pfam_id)

    #ADD LOGGER

def check_results(dir, pfam_id):
    if path.exists(dir + "/results"):
        if Pfama.objects.filter(pfama_acc=pfam_id).count() > 0:
            pfam = Pfama.objects.filter(pfama_acc=pfam_id)[0]
            pfam.sdb = True
            pfam.save()
            print(pfam_id)

class Command(BaseCommand):
    def handle(self, **options):
        dirs = glob(RESULTS_PATH + "*")
        for family_dir in dirs:
            pfam_id = family_dir.split('/')[-1]
            check_results(family_dir, pfam_id)
            #load(pfam_id)
