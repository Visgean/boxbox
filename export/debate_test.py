from models import *
from pytz import timezone


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



debata_id = 3964

debata = Debata.get(debata=debata_id)

neg = Debata_Tym.get(debata=debata_id, pozice=0)
aff = Debata_Tym.get(debata=debata_id, pozice=1)


# print [clovek.presvedcive for clovek in Clovek_Debata.filter(debata=debata_id)]



debate_data = {
        'date': convert_datetime(debata.datum),
        'location': debata.misto,
        'proposition': {
            'team': '',
            'speakers': {}
        },
        'opposition': {
            'team':'',
            'speakers': {}
        },
        'judges': [],
        'winner': 'proposition' if debata.vitez == 1 else 'opposition',
        'split': not bool(debata.presvedcive)
    }


proposiotion_order = {
    'a1': 1,
    'a2': 2,
    'a3': 3,
}

opposition_order = {
    'n1': 1,
    'n2': 2,
    'n3': 3,
}


for clovek in Clovek_Debata.filter(debata=debata_id):
    if clovek.role == 'r':
        debate_data['judges'].append({
            'human': '...',
            'decision': 'proposition' if clovek.rozhodnuti == 1 else 'opposition',
            'split': not bool(clovej.presvedcive)

        })
    elif clovek.role in proposiotion_order.keys():
        debate_data['proposition']['speakers'][proposiotion_order[clovek.role]] = {
            'human': 'clovek id',
            'points': clovek.kidy
        }
    elif clovek.role in opposition_order.keys():
        debate_data['opposition']['speakers'][opposition_order[clovek.role]] = {
            'human': 'clovek id',
            'points': clovek.kidy
        }

print debate_data
















