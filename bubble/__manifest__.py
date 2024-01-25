{
    'name': 'Bubble and OKR',
    'version': '15.1.1.0',
    'summary': 'Bubble and OKR',
    'sequence': -100,
    'description': """Buble and OKR Management""",
    'category': 'Hr',
    'website': 'https://www.rapsodoo.com',
    'depends': ['mail','web'],
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
        'views/okr_evaluation_type.xml',
        'views/menu.xml',
        'wizard/wizard.xml',
        'wizard/wizard_view_bubble.xml',
        'wizard/wizard_suggest_kr.xml',
        'data/data.xml'
       # 'views/asset.xml'
    ],
    'qweb': ['static/src/xml/bubble_widget.xml'],
    'assets': {
        'web.assets_backend': [
            '/bubble/static/src/xml/bubble_widget.xml',
            'https://cdn.babylonjs.com/babylon.js',
            '/bubble/static/src/js/app.js',
            '/bubble/static/src/js/bubble_widget.js',
            ],
          'web.assets_qweb': [
                '/bubble/static/src/xml/bubble_widget.xml',
            ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license':'OEEL-1'
}
