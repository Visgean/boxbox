import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError
from pytz import timezone
from multiprocessing.dummy import Pool as ThreadPool

from models import *

# rethink db settings:
RDB_HOST = 'localhost'
RDB_PORT = 28015
DEBATE_DB = 'debate'
DB_TABLES = ['organizations', 'competitions', 'tournaments', 'debates', 'motions', 'humans', 'clubs']
POOL_SIZE = 10



# debate speakers order keys are old names values are new names
PROPOSITION_ORDER = {
    'a1': ('1st', 1),
    'a2': ('2nd', 2),
    'a3': ('3rd', 3),
}

OPPOSITION_ORDER = {
    'n1': ('1st', 1),
    'n2': ('2nd', 2),
    'n3': ('3rd', 3),
}


def convert_date(date):
    """Convert date object so it can be used by rethinkdb if date is none than current date is to be used"""
    if not date:
        date = datetime.date.today()

    dt = datetime.datetime.combine(date, datetime.datetime.min.time())
    prague = timezone('Europe/Prague')
    return prague.localize(dt, is_dst=False)


def convert_datetime(dt):
    """Convert datetime object so it can be used by rethinkdb if date is none than current date is to be used"""
    if not dt:
        dt = dt.now()
    prague = timezone('Europe/Prague')
    return prague.localize(dt, is_dst=False)


def db_setup():
    """Setup rethinkdb and create all the tables that are going to be used."""
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)

    try:
        r.db_create(DEBATE_DB).run(connection)
    except RqlRuntimeError:  # lets crate a new and clean db.
        r.db_drop(DEBATE_DB).run(connection)
        r.db_create(DEBATE_DB).run(connection)

    connection.close()
    connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=DEBATE_DB)

    for table in DB_TABLES:
        r.db(DEBATE_DB).table_create(table).run(connection)
        print 'Table {0} created.'.format(table)
    connection.close()


def klub_export(klub):
    new_obj = r.table('clubs').insert({
        'name': klub.nazev,
        'short_name': klub.kratky_nazev,
        'description': klub.komentar,
        'location': klub.misto,
        'organization': adk_id,
        'members': [],
    }).run(conn)

    id_conversion['klub'][klub.klub] = new_obj['generated_keys'][0]


def clovek_export(clovek):
    new_obj = r.table('humans').insert({
        'name': clovek.jmeno,
        'surname': clovek.prijmeni,
        'birthdate': convert_date(clovek.narozen),
        'nickname': clovek.nick,
    }).run(conn)

    new_id = new_obj['generated_keys'][0]
    id_conversion['clovek'][clovek.clovek] = new_id

    if clovek.klub:
        klub_id = id_conversion['klub'][clovek.klub]
        r.table('clubs').get(klub_id).update(
            {'members': r.row['members'].append(new_id)}
        ).run(conn)


def tym_export(tym):
    new_obj = r.table('clubs').insert({
        'name': tym.nazev,
        'description': tym.komentar,
        'club': id_conversion['klub'][tym.klub],
        'members': [id_conversion['clovek'].get(clovek.clovek, None) for clovek in Clovek_Tym.filter(tym=tym.tym)]
    }).run(conn)

    id_conversion['klub'][tym.tym] = new_obj['generated_keys'][0]


def soutez_export(soutez):
    new_obj = r.table('competitions').insert({
        'language': soutez.jazyk,
        'name': soutez.nazev,
        'year': soutez.rocnik + 2000,
        'description': soutez.komentar,
        'type': 'cup',
        'organization': adk_id,
        'tournaments': [],
        'debates': []

    }).run(conn)

    id_conversion['soutez'][soutez.soutez] = new_obj['generated_keys'][0]


def liga_export(liga):
    new_obj = r.table('competitions').insert({
        'language': 'cs',
        'name': liga.nazev,
        'year': liga.rocnik + 2000,
        'description': liga.komentar,
        'type': 'league',
        'organization': adk_id,
        'tournaments': [],
        'debates': []
    }).run(conn)

    id_conversion['liga'][liga.liga] = new_obj['generated_keys'][0]


def turnaj_export(turnaj):
    new_obj = r.table('tournaments').insert({
        'name': turnaj.nazev,
        'date': {
            'from': convert_date(turnaj.datum_od),
            'to': convert_date(turnaj.datum_do)
        },
        'description': turnaj.komentar,
        'organization': adk_id,
        'debates': [],
    }).run(conn)

    new_id = new_obj['generated_keys'][0]
    id_conversion['turnaj'][turnaj.turnaj] = new_id

    if turnaj.liga:
        liga_id = id_conversion['liga'][turnaj.liga]
        r.table('competitions').get(liga_id).update(
            {'tournaments': r.row['tournaments'].append(new_id)}
        ).run(conn)

    if turnaj.soutez:
        soutez_id = id_conversion['soutez'][turnaj.soutez]
        r.table('competitions').get(soutez_id).update(
            {'tournaments': r.row['tournaments'].append(new_id)}
        ).run(conn)


def teze_sync(teze):
    new_obj = r.table('motions').insert({
        'motion': teze.tx,
        'motion_short': teze.tx_short,
        'language': teze.jazyk,
    }).run(conn)

    new_id = new_obj['generated_keys'][0]
    id_conversion['teze'][teze.teze] = new_id


def debata_sync(debata):
    prop = Debata_Tym.get(debata=debata.debata, pozice=1)
    opp = Debata_Tym.get(debata=debata.debata, pozice=0)

    debate_data = {
        'date': convert_datetime(debata.datum),
        'location': debata.misto,
        'motion': id_conversion['teze'][debata.teze],
        'proposition': {
            'speakers': {},
            'points': prop.body,
            'league_points': prop.liga_vytezek,
        },
        'opposition': {
            'speakers': {},
            'points': opp.body,
            'league_points': opp.liga_vytezek,
        },
        'judges': [],
        'winner': 'proposition' if debata.vitez == 1 else 'opposition',
        'split': not bool(debata.presvedcive)
    }

    if prop.tym and id_conversion['tym'].get(prop.tym, None):
        debate_data['proposition']['team'] = id_conversion['tym'].get(prop.tym, None)
    if opp.tym and id_conversion['tym'].get(opp.tym, None):
        debate_data['opposition']['team'] = id_conversion['tym'].get(opp.tym, None)

    for clovek in Clovek_Debata.filter(debata=debata.debata):
        if clovek.role == 'r':
            debate_data['judges'].append({
                'human': id_conversion['clovek'][clovek.clovek],
                'decision': 'proposition' if clovek.rozhodnuti == 1 else 'opposition',
                'split': not bool(clovek.presvedcive)
            })

        elif clovek.role in PROPOSITION_ORDER.keys():
            debate_data['proposition']['speakers'][PROPOSITION_ORDER[clovek.role][0]] = {
                'human': id_conversion['clovek'][clovek.clovek],
                'points': clovek.kidy,
                'order': PROPOSITION_ORDER[clovek.role][1]
            }
        elif clovek.role in OPPOSITION_ORDER.keys():
            debate_data['opposition']['speakers'][OPPOSITION_ORDER[clovek.role][0]] = {
                'human': id_conversion['clovek'][clovek.clovek],
                'points': clovek.kidy,
                'order': OPPOSITION_ORDER[clovek.role][1]
            }

    new_obj = r.table('debates').insert(debate_data).run(conn)
    new_id = new_obj['generated_keys'][0]
    id_conversion['debata'][debata.debata] = new_id

    if debata.turnaj:
        r.table('tournaments').get({'id': id_conversion['turnaj'][debata.turnaj]}).update({
            'debates': r.row['debates'].append(new_id)
        }).run(conn)

    if debata.soutez:
        r.table('competitions').get({'id': id_conversion['soutez'][debata.soutez]}).update({
            'debates': r.row['debates'].append(new_id)
        }).run(conn)



db_setup()
connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=DEBATE_DB)

# adk organization
adk_id = r.table('organizations').insert({
    'abbr': 'ADK',
    'name': u'Asociace debatnich klubu'
}).run(connection)['generated_keys'][0]


# old id: new id.
id_conversion = {table: {} for table in ['soutez', 'liga', 'clovek', 'klub', 'turnaj', 'teze', 'debata', 'tym']
                 # 'organization':{
                 # greyboxid:rethinkdbid
                 # }
}






class RethinkWorker(ThreadPool):
    def __init__(self):
        ???
        super(RethinkWorker, self).__init__()
























