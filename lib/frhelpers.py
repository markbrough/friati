
# -*- coding: UTF-8 -*-

FR_STATUSES = {
            'en cours': '2',
            'termin\xe9': '3',
            'termin\xc3\xa9': '3',
            'achev\xe9': '3',
            'achev\xc3\xa9': '3'
        }

STATUSCODES = {
            '1': 'Pipeline/identification',
            '2': 'Implementation',
            '3': 'Completion',
            '4': 'Post-completion',
            '5': 'Cancelled'
        }

FR_ORGS = {
            'afd': 'FR-3',
            'mae': 'FR-6',
            'scac': 'FR-99',
            'scac et afd': 'FR-3'
}

FR_ORGS_CODES = {
            'FR-3': 'AFD',
            'FR-6': 'MAE',
            'FR-99': 'SCAC'
}

FINANCETYPES = {
            "": {
                'code': '',
                'text': ''
            },
            "ACTION": {
                'code': '500',
                'text': 'EQUITY'
            },
            "GARANTIES DONNEES": {
                'code': '900',
                'text': 'OTHER SECURITIES/CLAIMS'
            },
            "PRET": {
                'code': '400',
                'text': 'LOAN'
            },
            "SUBVENTION": {
                'code': '100',
                'text': 'GRANT'
            }
        }

FR_SECTORS = {
    "": "",
    "Agriculture et sécurité alimentaire": "31100",
    "Eau et assainissement": "14000",
    "Education": "11100",
    "Environnement et ressources naturelles": "41000",
    "Hors secteurs CICID": "99810",
    "Infrastructures et développement urbain": "21000",
    "Santé et lutte contre le sida": "12200",
    "Secteur productif": "32100"
}

SECTORS = {
    "": "",
    "31100": "Agriculture",
    "14000": "Water and sanitation",
    "11100": "Education",
    "41000": "Environment",
    "99810": "Sectors not specified",
    "21000": "Infrastructure",
    "12200": "Health",
    "32100": "Industry"    
}

CICID_SECTORS = {
    u"Sant\xe9": "1",
    u"\xc9ducation et formation professionnelle": "2",
    u"Agriculture et s\xe9curit\xe9 alimentaire": "3",
    u"agriculture et s\xe9curit\xe9 alimentaire": "3",
    u"D\xe9veloppement durable": "4",
    u"Soutien \xe0 la croissance" : "5",
    u"Gouvernement et soci\xe9t\xe9 civile": "6",
    "Autre": "7"
}
