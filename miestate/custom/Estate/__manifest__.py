# -*- coding: utf-8 -*-
{
    'name': 'estate',
    'summary': "tarea ejercicio",
    'description': """
Long description of module's purpose
    """,
    'author': "George",
    'website': "https://www.nadie.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}

