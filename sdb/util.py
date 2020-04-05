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
        pos1 = seq2alignPosition(msa[seqname], b_start, s_start)
        pos2 = seq2alignPosition(msa[seqname], b_end, s_start)

        if pos1 > 0 and pos2 > 0:
            print(seqname + " " + str(b_start) + " " + str(b_end))
            bonds.add((pos1, pos2))

    return bonds

def parseSites(pfam_id, msa):
    sites = set()

    sql = sites_SQL.format(pfam_id=pfam_id)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    for name, s_start, s_end, residue, type, annotation in result:
        seqname = name + "/" + str(s_start) + "-" + str(s_end)
        pos = seq2alignPosition(msa[seqname], residue, s_start)

        if pos > 0:
            sites.add((pos, type, annotation))

    return sites

# def generateProtVista2(pfam_id):


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


def generate_protvista_js(conf):
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
