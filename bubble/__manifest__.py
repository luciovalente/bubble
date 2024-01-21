{
    'name': 'Bubble and OKR',
    'version': '15.1.1.0',
    'summary': 'Gestione delle Buble',
    'sequence': -100,
    'description': """Gestione delle Bolle""",
    'category': 'Hr',
    'website': 'https://www.rapsodoo.com',
    'depends': ['mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/bubble_role_view.xml',
        'views/bubble_type_view.xml',
        'views/bubble_view.xml',
        'views/objective_view.xml',
        'views/okr_view.xml',
        'views/okr_result.xml',
        'views/okr_evaluation.xml',
       
        'data/data.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
