from django.db import models

class Family(models.Model):
    pfam_id = models.CharField(db_index=True, max_length=7,primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    sequences = models.ManyToManyField('Offset')

    def __str__(self):
        return self.pfam_id

class Conformation(models.Model):
    score = models.FloatField()#Cut value
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    network = models.TextField()

class Community(models.Model):
    residues = models.TextField()
    score = models.FloatField()#Real score
    size = models.IntegerField()#NOT USED
    conformation = models.ForeignKey(Conformation,on_delete=models.CASCADE)

    def get_residues(self):
        return self.residues.split()

    #def getResiduesList


class Sequence(models.Model):
    accession = models.CharField(db_index=True, max_length=25,primary_key=True)

    def __str__(self):
        return self.accession

class Offset(models.Model):
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    sequence_fk = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    sequence = models.TextField()

    def __str__(self):
        return "/" + str(self.pos_from) + "-" + str(self.pos_to)
