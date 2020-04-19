from sdb.models import *
from django.db import connection

refs_SQL = """
SELECT literature_reference.auto_lit,
	  order_added,
	  pmid,
	  title,
	  literature_reference.author,
	  journal
FROM   pfamA,
	  pfamA_literature_reference,
	  literature_reference
WHERE  pfamA_id = '{pfam_id}'
AND    pfamA.pfamA_acc = pfamA_literature_reference.pfamA_acc 
AND    pfamA_literature_reference.auto_lit = literature_reference.auto_lit;
"""

disulfide_SQL = """
SELECT pfamseq_id,seq_start,seq_end,bond_start,bond_end FROM pfamseq_disulphide as t1,
(SELECT pfamseq_acc, seq_start, seq_end FROM pfamA_reg_full_significant WHERE pfamA_reg_full_significant.pfamA_acc =(
SELECT pfamA_acc FROM pfamA WHERE pfamA_id = "{pfam_id}")) as t2,
pfamseq as t3
WHERE t1.pfamseq_acc=t2.pfamseq_acc
and t3.pfamseq_acc = t1.pfamseq_acc
AND bond_start >= seq_start
AND bond_end <= seq_end
"""

sites_SQL = """
SELECT pfamseq_id,seq_start,seq_end,residue,auto_markup,annotation FROM pfamseq_markup as t1,
(SELECT pfamseq_acc, seq_start, seq_end FROM pfamA_reg_full_significant WHERE pfamA_reg_full_significant.pfamA_acc =(
SELECT pfamA_acc FROM pfamA WHERE pfamA_id = "{pfam_id}")) as t2,
pfamseq as t3
WHERE t1.pfamseq_acc=t2.pfamseq_acc
and t3.pfamseq_acc = t1.pfamseq_acc
and (t1.auto_markup=1 or t1.auto_markup=4)
"""

disulfide_sequence_SQL = """
SELECT
    (@cnt := @cnt + 1) AS id,
    t.*
FROM pfam_32_0.pfamseq_disulphide AS t
CROSS JOIN (SELECT @cnt := 0) AS dummy
WHERE t.pfamseq_acc='{seqname}'
"""

sites_sequence_SQL = """
SELECT
    (@cnt := @cnt + 1) AS id,
    t.*
FROM pfam_32_0.pfamseq_markup AS t
CROSS JOIN (SELECT @cnt := 0) AS dummy
WHERE t.pfamseq_acc='{seqname}'
"""

region_sequence_SQL = """
SELECT *
FROM pfam_32_0.other_reg AS t
WHERE t.pfamseq_acc='{seqname}'
"""


def getReferences(pfam_id):
    sql = refs_SQL.format(pfam_id=pfam_id)
    references = LiteratureReference.objects.raw(sql)
    refs = []

    for ref in references:
        text = ref.author + ref.title + ref.journal
        pmid = ref.pmid
        refs.append((text, pmid))

    return refs


def seq2alignPosition(sequence, pos, offset):
    pos -= (offset - 1)
    seqpos = 0
    amspos = 1
    found = False
    for i, aa in enumerate(sequence):
        if aa != '-' and aa != '.':
            seqpos += 1
            if seqpos == pos:
                found = True
                amspos = i + 1
    if found:
        return amspos
    else:
        return -1


def parseDisulfide(pfam_id, msa):
    bonds = set()

    sql = disulfide_SQL.format(pfam_id=pfam_id)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    for name, s_start, s_end, b_start, b_end in result:
        seqname = name + "/" + str(s_start) + "-" + str(s_end)
        if seqname in msa:
            pos1 = seq2alignPosition(msa[seqname], b_start, s_start)
            pos2 = seq2alignPosition(msa[seqname], b_end, s_start)

            if pos1 > 0 and pos2 > 0:
                bonds.add((pos1, pos2, ''))

    return bonds

def parseSites(pfam_id, msa):
    sites = (set(),set())#0 - Active, 1 - Metal Ion

    sql = sites_SQL.format(pfam_id=pfam_id)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    for name, s_start, s_end, residue, type, annotation in result:
        seqname = name + "/" + str(s_start) + "-" + str(s_end)
        if seqname in msa:
            pos = seq2alignPosition(msa[seqname], residue, s_start)

            if pos > 0:
                if type == 1:
                    sites[0].add((pos, pos, annotation))
                elif type == 4:
                    sites[1].add((pos, pos, annotation))

    return sites

def parseCommunity(community):
    comm = set()

    for residue in community:
        aa = residue[0]
        pos = int(residue[1:])
        comm.add((pos,pos,residue))

    return comm

def createAddFeatureJS(name, className, color, type, filter, data):
    js = ""

    if len(data) > 0:
        js += "ft2.addFeature({"
        js += "name: \"" + name + "\","
        js += "className: \"" + className + "\","
        js += "color: \"" + color + "\","
        js += "type: \"" + type + "\","
        js += "filter: \"" + filter + "\","
        js += "data: ["

        for pos1, pos2, desc in data:
            if desc == "":
                js += "{x:" + str(pos1) + ",y:" + str(pos2) + "},"
            else:
                js += "{x:" + str(pos1) + ",y:" + str(pos2) + ",description:\"" + desc + "\"},"
        js += "]});";

    return js

def generateProtVista(pfam, msa, conformation):
    js = ""

    js += "var ft2 = new FeatureViewer(\"" + pfam.full_consensus + "\",\"#fv1\", {"
    js += "showAxis: true,"
    js += "showSequence: true,"
    js += "brushActive: true,"
    js += "toolbar:false,"
    js += "bubbleHelp:true,"
    js += "zoomMax:10"
    js += "});"

    bonds = parseDisulfide(pfam.pfama_id,msa)
    active_sites, ion_sites = parseSites(pfam.pfama_id,msa)

    communities = conformation.community_set.all()
    N = len(communities)
    for i,comm in enumerate(communities):
        residues = comm.get_residues()
        community = parseCommunity(residues)
        js += createAddFeatureJS("Community " + str(i+1), "comm", pickColor(i), "rect", "type1", community)

    js += createAddFeatureJS("Disulfide","disulfide",pickColor(N),"path","type1",bonds)
    js += createAddFeatureJS("Active Site", "active", pickColor(N+1), "rect", "type1", active_sites)
    js += createAddFeatureJS("Metal Binding", "metal", pickColor(N+2), "rect", "type1", ion_sites)

    return js

def generateProtVistaSequence(sequence):
    uniprot = Uniprot.objects.get(uniprot_acc=sequence)
    js = ""

    js += "var ft2 = new FeatureViewer(\"" + uniprot.sequence.decode("utf-8")  + "\",\"#fv1\", {"
    js += "showAxis: true,"
    js += "showSequence: true,"
    js += "brushActive: true,"
    js += "toolbar:false,"
    js += "bubbleHelp:true,"
    js += "zoomMax:10"
    js += "});"

    #Disulfide
    sql = disulfide_sequence_SQL.format(seqname=sequence)
    results = PfamseqDisulphide.objects.raw(sql)
    bonds = []
    for result in results:
        bonds.append((result.bond_start,result.bond_end,''))

    #Sites
    sql = sites_sequence_SQL.format(seqname=sequence)
    results = PfamseqMarkup.objects.raw(sql)
    sites = set()
    for result in results:
        if result.auto_markup < 4:
            sites.add((result.residue,result.residue,"Active site"))
        else:
            sites.add((result.residue, result.residue, result.annotation))

    #Other regions
    sql = region_sequence_SQL.format(seqname=sequence)
    coiled_coil = set()
    disorder = set()
    low_complexity = set()
    sig_p = set()
    transmembrane = set()
    results = OtherReg.objects.raw(sql)
    for result in results:
        if result.type_id == 'coiled_coil':
            coiled_coil.add((result.seq_start, result.seq_end, ''))
        elif result.type_id == 'disorder':
            disorder.add((result.seq_start, result.seq_end, ''))
        elif result.type_id == 'low_complexity':
            low_complexity.add((result.seq_start, result.seq_end, ''))
        elif result.type_id == 'sig_p':
            sig_p.add((result.seq_start, result.seq_end, ''))
        elif result.type_id == 'transmembrane':
            transmembrane.add((result.seq_start, result.seq_end, ''))

    # Pfams
    pfams = []
    regions = UniprotRegFull.objects.filter(uniprot_acc=sequence)
    unique_pfams = regions.values('pfama_acc').distinct()
    for current_pfam in unique_pfams:
        current_pfam_id = current_pfam['pfama_acc']
        interval_list = []
        pfam_set = regions.filter(pfama_acc=current_pfam_id).order_by("seq_start")
        for region in pfam_set:
            interval_list.append((region.seq_start, region.seq_end, region.pfama_acc))
        if len(interval_list) > 0:
            pfams.append((current_pfam_id,interval_list))

    #Pfams
    # pfams = []
    # regions = UniprotRegFull.objects.filter(uniprot_acc=sequence)
    # for region in regions:
    #     pfams.append((region.seq_start, region.seq_end, region.pfama_acc))


    js += createAddFeatureJS("Disulfide", "disulfide", pickColor(0), "path", "type1", bonds)
    js += createAddFeatureJS("Coiled coil", "active", pickColor(1), "rect", "type1", coiled_coil)
    js += createAddFeatureJS("Sites", "active", pickColor(2), "rect", "type1", sites)
    js += createAddFeatureJS("Disorder", "active", pickColor(3), "rect", "type1", disorder)
    js += createAddFeatureJS("Low complexity", "active", pickColor(4), "rect", "type1", low_complexity)
    js += createAddFeatureJS("Signal peptide", "active", pickColor(5), "rect", "type1", sig_p)
    js += createAddFeatureJS("Transmembrane", "active", pickColor(6), "rect", "type1", transmembrane)
    #js += createAddFeatureJS("Pfam", "active", pickColor(7), "rect", "type1", pfams)

    for i,(pfam_id,pfam) in enumerate(pfams):
        js += createAddFeatureJS(pfam_id, "active", pickColor(7+i), "rect", "type1", pfam)

    return js

def getPfamList(start, end):
    total = Pfama.objects.count()

    if end > total:
        end = total

    return Pfama.objects.all()[start:end]


kelly_colors_hex = [
    "#FFB300",  # Vivid Yellow
    "#803E75",  # Strong Purple
    "#FF6800",  # Vivid Orange
    "#A6BDD7",  # Very Light Blue
    "#C10020",  # Vivid Red
    "#CEA262",  # Grayish Yellow
    "#817066",  # Medium Gray

    # The following don't work well for people with defective color vision
    "#007D34",  # Vivid Green
    "#F6768E",  # Strong Purplish Pink
    "#00538A",  # Strong Blue
    "#FF7A5C",  # Strong Yellowish Pink
    "#53377A",  # Strong Violet
    "#FF8E00",  # Vivid Orange Yellow
    "#B32851",  # Strong Purplish Red
    "#F4C800",  # Vivid Greenish Yellow
    "#7F180D",  # Strong Reddish Brown
    "#93AA00",  # Vivid Yellowish Green
    "#593315",  # Deep Yellowish Brown
    "#F13A13",  # Vivid Reddish Orange
    "#232C16",  # Dark Olive Green
]


def pickColor(i):
    if i < 20:
        return kelly_colors_hex[i]
    else:
        return kelly_colors_hex[i % 20]


def generate_protvista_js2(conf):
    js = ""
    temp_seq = Offset.objects.all()[0]

    js += "var ft2 = new FeatureViewer(\"" + temp_seq.sequence + "\",\"#fv1\", {";
    js += "showAxis: true,";
    js += "showSequence: true,";
    js += "brushActive: true,";
    js += "toolbar:false,";
    js += "bubbleHelp:true,";
    js += "zoomMax:10";
    js += "});";

    for i, comm in enumerate(conf.community_set.all()):
        color = pickColor(i)

        js += "ft2.addFeature({";
        js += "name: \"Community  " + str(i + 1) + "\",";
        js += "className: \"comm" + str(i + 1) + "\",";
        js += "color: \"" + color + "\",";
        js += "type: \"rect\",";
        js += "filter: \"type1\",";
        js += "data: [";

        residues = comm.get_residues()

        for residue in residues:
            aa = residue[0]
            pos = residue[2:]

            js += "{x:" + pos + ",y:" + pos + ",description:\"" + aa + "\"},";

        js += "]});";

    return js;


def getFasta(pfam):
    js = "var fasta=\""

    sequences = pfam.sequences.all()

    for offset in sequences:
        seqname = offset.sequence_fk.accession + str(offset)
        sequence = offset.sequence

        js += ">" + seqname + "\\n" + sequence + "\\n";

    js += "\";var seqs=msa.io.fasta.parse(fasta),opts={el:msaview,seqs:seqs,conf:{debug:false},vis:{conserv:!0,overviewbox:!1,seqlogo:!0}},m=msa(opts);m.render(),m.g.zoomer.set('alignmentHeight',400),m.g.zoomer.set('labelNameLength',190);m.g.zoomer.set(\"alignmentWidth\", \"auto\");m.g.config.set(\"debug\",false);var defMenu=new msa.menu.defaultmenu({el:menuDiv,msa:m});defMenu.render();";
    return js
