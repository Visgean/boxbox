from peewee import *

database = MySQLDatabase('debatovani', **{'passwd': '12345', 'host': '10.0.0.100', 'port': 3306, 'user': 'debatovani'})


class BaseModel(Model):
    class Meta:
        database = database

class Clovek(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')

    jmeno = CharField(max_length=26)
    prijmeni = CharField(max_length=40)
    nick = CharField(max_length=40, null=True)
    narozen = DateField(null=True)
    klub = IntegerField(null=True, db_column='klub_ID')

    odznak = CharField(max_length=3, null=True)

    clen = IntegerField()
    clen_do = IntegerField()
    debater = IntegerField()
    dostal = IntegerField()
    komentar = TextField(null=True)
    prava_debaty = IntegerField()
    prava_kluby = IntegerField()
    prava_lidi = IntegerField()
    prava_souteze = IntegerField()

    class Meta:
        db_table = 'clovek'


class Turnaj(BaseModel):
    datum_do = DateField()
    datum_od = DateField()
    komentar = TextField(null=True)
    liga = IntegerField(null=True, db_column='liga_ID')
    nazev = CharField(max_length=170)
    soutez = IntegerField(db_column='soutez_ID')
    turnaj = PrimaryKeyField(db_column='turnaj_ID')

    class Meta:
        db_table = 'turnaj'

class Klub(BaseModel):
    klub = PrimaryKeyField(db_column='klub_ID')
    komentar = TextField(null=True)
    kratky_nazev = CharField(max_length=21)
    misto = CharField(max_length=170, null=True)
    nazev = CharField(max_length=170)

    class Meta:
        db_table = 'klub'




class Clovek_Debata(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    debata = IntegerField(db_column='debata_ID')
    kidy = IntegerField(null=True)
    presvedcive = IntegerField(null=True)
    role = CharField(max_length=2)
    rozhodnuti = IntegerField(null=True)

    class Meta:
        db_table = 'clovek_debata'

class Clovek_Debata_Ibody(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    debata = IntegerField(db_column='debata_ID')
    ibody = DecimalField()
    rocnik = IntegerField()
    role = CharField(max_length=11)

    class Meta:
        db_table = 'clovek_debata_ibody'

class Clovek_Ibody(BaseModel):
    clovek = IntegerField(db_column='clovek_ID')
    clovek_ibody = PrimaryKeyField(db_column='clovek_ibody_ID')
    ibody = DecimalField()
    rocnik = IntegerField()
    tx = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'clovek_ibody'

class Clovek_Klub(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    klub = IntegerField(db_column='klub_ID')
    rocnik = IntegerField()
    role = CharField(max_length=1)

    class Meta:
        db_table = 'clovek_klub'

class Clovek_Turnaj(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    mocnost = IntegerField()
    role = CharField(max_length=1)
    turnaj = IntegerField(db_column='turnaj_ID')

    class Meta:
        db_table = 'clovek_turnaj'

class Clovek_Tym(BaseModel):
    aktivni = IntegerField()
    clovek = PrimaryKeyField(db_column='clovek_ID')
    tym = IntegerField(db_column='tym_ID')

    class Meta:
        db_table = 'clovek_tym'

class Debata(BaseModel):
    achtung = IntegerField()
    datum = DateTimeField()
    debata = PrimaryKeyField(db_column='debata_ID')
    komentar = TextField(null=True)
    liga_kidy = IntegerField(null=True)
    misto = CharField(max_length=170, null=True)
    presvedcive = IntegerField()
    soutez = IntegerField(db_column='soutez_ID')
    teze = IntegerField(db_column='teze_ID')
    turnaj = IntegerField(null=True, db_column='turnaj_ID')
    vitez = IntegerField()

    class Meta:
        db_table = 'debata'

class Debata_Tym(BaseModel):
    body = IntegerField(null=True)
    debata = PrimaryKeyField(db_column='debata_ID')
    liga_vytezek = DecimalField(null=True)
    pozice = IntegerField()
    tym = IntegerField(db_column='tym_ID')

    class Meta:
        db_table = 'debata_tym'

class Kategorie(BaseModel):
    kategorie = PrimaryKeyField(db_column='kategorie_ID')
    nazev = CharField(max_length=255)

    class Meta:
        db_table = 'kategorie'

class Kategorie_Teze(BaseModel):
    kategorie = IntegerField(db_column='kategorie_ID')
    teze = IntegerField(db_column='teze_ID')

    class Meta:
        db_table = 'kategorie_teze'


class Kontakt(BaseModel):
    clovek = IntegerField(db_column='clovek_ID')
    druh = CharField(max_length=7)
    kontakt = PrimaryKeyField(db_column='kontakt_ID')
    tx = CharField(max_length=170)
    viditelnost = IntegerField()

    class Meta:
        db_table = 'kontakt'

class Liga(BaseModel):
    komentar = TextField(null=True)
    liga = PrimaryKeyField(db_column='liga_ID')
    nazev = CharField(max_length=170)
    rocnik = IntegerField()

    class Meta:
        db_table = 'liga'

class Liga_Tym(BaseModel):
    liga = PrimaryKeyField(db_column='liga_ID')
    liga_vytezek = DecimalField()
    skrtnute_debaty = CharField(max_length=170, null=True)
    tym = IntegerField(db_column='tym_ID')

    class Meta:
        db_table = 'liga_tym'

class Login(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    password = CharField(max_length=32)
    username = CharField(max_length=22)

    class Meta:
        db_table = 'login'

class Rozhodci(BaseModel):
    clovek = PrimaryKeyField(db_column='clovek_ID')
    format = CharField(max_length=14, null=True)
    jazyk = CharField(max_length=11, null=True)
    misto = CharField(max_length=170, null=True)
    rocnik = IntegerField()

    class Meta:
        db_table = 'rozhodci'

class Soutez(BaseModel):
    jazyk = CharField(max_length=2)
    komentar = TextField(null=True)
    nazev = CharField(max_length=170)
    rocnik = IntegerField()
    soutez = PrimaryKeyField(db_column='soutez_ID')
    zamceno = IntegerField()

    class Meta:
        db_table = 'soutez'

class Soutez_Teze(BaseModel):
    soutez = PrimaryKeyField(db_column='soutez_ID')
    teze = IntegerField(db_column='teze_ID')

    class Meta:
        db_table = 'soutez_teze'

class Teze(BaseModel):
    jazyk = CharField(max_length=2)
    komentar = TextField(null=True)
    teze = PrimaryKeyField(db_column='teze_ID')
    tx = CharField(max_length=170)
    tx_short = CharField(max_length=26)

    class Meta:
        db_table = 'teze'

class Teze_Jazyk(BaseModel):
    jazyk = CharField(max_length=2)
    teze = IntegerField(db_column='teze_ID')
    tx = CharField(max_length=170)
    tx_short = CharField(max_length=26)

    class Meta:
        db_table = 'teze_jazyk'

class Tezenove(BaseModel):
    jazyk = CharField(max_length=2)
    komentar = TextField(null=True)
    teze = PrimaryKeyField(db_column='teze_ID')
    tx = CharField(max_length=170)
    tx_short = CharField(max_length=26)

    class Meta:
        db_table = 'tezenove'


class Tym(BaseModel):
    klub = IntegerField(db_column='klub_ID')
    komentar = TextField(null=True)
    nazev = CharField(max_length=170)
    tym = PrimaryKeyField(db_column='tym_ID')

    class Meta:
        db_table = 'tym'

class User(BaseModel):
    password = CharField(max_length=60)
    role = CharField(max_length=20)
    username = CharField(max_length=50)

    class Meta:
        db_table = 'user'

