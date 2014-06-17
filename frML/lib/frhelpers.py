
# -*- coding: UTF-8 -*-

FR_STATUSES = {
    'en cours': '2',
    'ex\xc3\xa9cution': '2',
    'termin\xe9': '3',
    'termin\xc3\xa9': '3',
    'achev\xe9': '3',
    'achev\xc3\xa9': '3'
}

STATUSCODES = {
    '1': 'Planification',
    '2': 'Actif',
    '3': 'Finalisation',
    '4': 'Fermé',
    '5': 'Annulé'
}

FR_ORGS = {
    u'afd': 'FR-3',
    u'mae': 'FR-6',
    u'scac': 'FR-99',
    u"service de coop\xc3\xa9ration et d'action culturelle": 'FR-99',
    u"service de coop\xe9ration et d'action culturelle": 'FR-99',
    u'scac et afd': 'FR-3'
}

FR_ORGS_CODES = {
    'FR-3': 'AFD',
    'FR-6': 'MAE',
    'FR-99': u"Service de Coop\xe9ration et d'Action Culturelle"
}

FINANCETYPES = {
    "": {
        'code': '',
        'text': ''
    },
    u"110 - Don sauf réorganisation de la dette": {
        'code': '110',
        'text': "Don sauf réorganisation de la dette"
    },
    u"410 - Prêt d'aide sauf réorganisation de la dette": {
        'code': '410',
        'text': "Prêt d'aide sauf réorganisation de la dette"
    },
    u"610 - Remise de dette : créances d'APD (P)": {
        'code': '610',
        'text': "Remise de dette : créances d'APD (P)"
    },
    u"610 - Remise de dette : créances d'APD (I)": {
        'code': '610',
        'text': "Remise de dette : créances d'APD (I)"
    }
}

AIDTYPES = {
    "A01 - Soutien budgétaire général": {
        'code': "A01",
        'text': "Soutien budgétaire général",
    },
    "A02 - Soutien budgétaire sectoriel": {
        "code": "A02",
        "text": "Soutien budgétaire sectoriel",
    },
    "B01 - Contributions aux budgets réguliers des ONG, autres organismes privés, partenariats public-privé (PPP) et instituts de recherche": {
        "code": "B01",
        "text": "Contributions aux budgets réguliers des ONG, autres organismes privés, partenariats public-privé (PPP) et instituts de recherche",
    },
    "B02 - Contributions aux budgets réguliers des institutions multilatérales": {
        "code": "B02",
        "text": "Contributions aux budgets réguliers des institutions multilatérales",
    },
    "B03 - Contributions à des programmes ou fonds à objectif spécifique gérés par des organisations internationales (multilatérales, ONGI)": {
        "code": "B03",
        "text": "Contributions à des programmes ou fonds à objectif spécifique gérés par des organisations internationales (multilatérales, ONGI)",
    },
    "B04 - Fonds communs/financements groupés": {
        "code": "B04",
        "text": "Fonds communs/financements groupés",
    },
    "C01  - Interventions de type projet": {
        "code": "C01",
        "text": "Interventions de type projet",
    },
    "D01 - Personnel du pays donneur": {
        "code": "D01",
        "text": "Personnel du pays donneur",
    },
    "D02 - Autres formes d’assistance technique ": {
        "code": "D02",
        "text": "Autres formes d’assistance technique",
    },
    "E01 - Bourses/formations dans le pays donneur": {
        "code": "E01",
        "text": "Bourses/formations dans le pays donneur",
    },
    "E02 - Coûts imputés des étudiants": {
        "code": "E02",
        "text": "Coûts imputés des étudiants",
    },
    "F01 - Allégement de la dette": {
        "code": "F01",
        "text": "Allégement de la dette",
    },
    "G01 - Frais administratifs non inclus ailleurs": {
        "code": "G01",
        "text": "Frais administratifs non inclus ailleurs",
    },
    "H01 - Sensibilisation au développement ": {
        "code": "H01", 
        "text": "Sensibilisation au développement",
    },

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
