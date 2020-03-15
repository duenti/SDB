from sdb.models import *

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



#def calculateCovMatrix(conf,i):
#    comm = conf.community_set.all()[i]
#    residues = comm.get_residues()
