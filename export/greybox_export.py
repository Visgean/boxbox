import datetime
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError
from models import *
from pytz import timezone


RDB_HOST = 'localhost'
RDB_PORT = 28015
DEBATE_DB = 'debate'
DB_TABLES = ['organizations', 'competitions', 'tournaments', 'debates', 'motions', 'humans', 'clubs']


PROPOSITION_ORDER = {
    'a1': 1,
    'a2': 2,
    'a3': 3,
    }

OPPOSITION_ORDER = {
    'n1': 1,
    'n2': 2,
    'n3': 3,
}

def convert_date(date):
    '''Convert date object so it can be used by rethinkdb if date is none than current date is to be used'''
    if not date:
        date = datetime.date.today()

    dt = datetime.datetime.combine(date, datetime.datetime.min.time())
    prague = timezone('Europe/Prague')

    return prague.localize(dt, is_dst=False)

def convert_datetime(datetime):
    '''Convert date object so it can be used by rethinkdb if date is none than current date is to be used'''
    if not datetime:
        datetime = datetime.now()

    prague = timezone('Europe/Prague')

    return prague.localize(datetime, is_dst=False)


def db_setup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)

    try:
        r.db_create(DEBATE_DB).run(connection)
    except RqlRuntimeError:                         # lets crate a new and clean db.
        r.db_drop(DEBATE_DB).run(connection)
        r.db_create(DEBATE_DB).run(connection)

    connection.close()
    connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=DEBATE_DB)

    for table in DB_TABLES:
        r.db(DEBATE_DB).table_create(table).run(connection)
        print 'Table {0} created.'.format(table)
    connection.close()





#db_setup()


connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=DEBATE_DB)
connection.repl()


adk_id = r.table('organizations').insert({
    'abbr': 'ADK',
    'name': u'Asociace debatnich klubu'
}).run()['generated_keys'][0]


id_conversion = {table:{} for table in ['soutez', 'liga', 'clovek', 'klub', 'turnaj']
    # 'organization':{
    # greyboxid:rethinkdbid
    # }
}

print 'Syncing humans'
for klub in Klub.select():
    print klub.nazev
    new_obj = r.table('clubs').insert({
            'name': klub.nazev,
            'short_name': klub.kratky_nazev,
            'description': klub.komentar,
            'location': klub.misto,
            'organization': adk_id,
            'members': []
        }).run()

    id_conversion['klub'][klub.klub] = new_obj['generated_keys'][0]


print 'Syncing humans'

for clovek in Clovek.select():
    print clovek.jmeno
    new_obj = r.table('humans').insert({
            'name': clovek.jmeno,
            'surname': clovek.prijmeni,
            'birthdate': convert_date(clovek.narozen),
            'nickname': clovek.nick,
        }).run()


    new_id = new_obj['generated_keys'][0]
    id_conversion['clovek'][clovek.clovek] = new_id

    if clovek.klub:
        klub_id = id_conversion['klub'][clovek.klub]
        r.table('clubs').get(klub_id).update(
                {'members': r.row['members'].append(new_id)}
            ).run()



print 'Syncing cups'
for soutez in Soutez.select():
    print soutez.nazev
    new_obj = r.table('competitions').insert({
            'language': soutez.jazyk,
            'name': soutez.nazev,
            'year': soutez.rocnik+2000,
            'description': soutez.komentar,
            'type':'cup',
            'organization': adk_id,
            'tournaments':[]

        }).run()

    id_conversion['soutez'][soutez.soutez] = new_obj['generated_keys'][0]

print 'Syncing leagues'
for liga in Liga.select():
    print liga.nazev
    new_obj = r.table('competitions').insert({
            'language': 'cs',
            'name': liga.nazev,
            'year': liga.rocnik+2000,
            'description': liga.komentar,
            'type': 'league',
            'organization': adk_id,
            'tournaments':[]
        }).run()

    id_conversion['liga'][liga.liga] = new_obj['generated_keys'][0]


print 'Syncing tournaments'
for turnaj in Turnaj.select():
    print turnaj.nazev
    new_obj = r.table('tournaments').insert({
        'name': turnaj.nazev,
        'date': {
            'from': convert_date(turnaj.datum_od),
            'to': convert_date(turnaj.datum_do)
        },
        'description': turnaj.komentar,
        'organization': adk_id,
        }).run()

    new_id = new_obj['generated_keys'][0]
    id_conversion['turnaj'][turnaj.turnaj] = new_id

    if turnaj.liga:
        liga_id = id_conversion['liga'][turnaj.liga]
        r.table('competitions').get(liga_id).update(
            {'tournaments': r.row['tournaments'].append(new_id)}
        ).run()

    if turnaj.soutez:
        soutez_id = id_conversion['soutez'][turnaj.soutez]
        r.table('competitions').get(soutez_id).update(
            {'tournaments': r.row['tournaments'].append(new_id)}
        ).run()


for teze in list(Tezenove.select())+list(Teze.select()):
    new_obj = r.table('motions').insert({
        'motion': teze.tx,
        'motion_short': teze.tx_short,
        'language': teze.jazyk,
    })

    new_id = new_obj['generated_keys'][0]
    id_conversion['teze'][teze.teze] = new_id



for debata in Debata.select():
    prop = Debata_Tym.get(debata=debata.debata, pozice=1)
    opp = Debata_Tym.get(debata=debata.debata, pozice=0)

    debate_data = {
        'date': convert_datetime(debata.datum),
        'location': debata.misto,
        'motion'
        'proposition': {
            'team': id_conversion['tym'][prop.tym],
            'speakers': {},
            'points': prop.body,
            'league_points': prop.liga_vytezek,

        },
        'opposition': {
            'team':id_conversion['tym'][opp.tym],
            'speakers': {},
            'points': opp.body,
            'league_points': opp.liga_vytezek,
        },
        'judges': [],
        'winner': 'proposition' if debata.vitez == 1 else 'opposition',
        'split': not bool(debata.presvedcive)
    }

    for clovek in Clovek_Debata.filter(debata=debata.debata):
        if clovek.role == 'r':
            debate_data['judges'].append({
                'human': '...',
                'decision': 'proposition' if clovek.rozhodnuti == 1 else 'opposition',
                'split': not bool(clovek.presvedcive)
            })
            
        elif clovek.role in PROPOSITION_ORDER.keys():
            debate_data['proposition']['speakers'][PROPOSITION_ORDER[clovek.role]] = {
                'human': 'clovek id',
                'points': clovek.kidy
            }
        elif clovek.role in OPPOSITION_ORDER.keys():
            debate_data['opposition']['speakers'][OPPOSITION_ORDER[clovek.role]] = {
                'human': 'clovek id',
                'points': clovek.kidy
            }








