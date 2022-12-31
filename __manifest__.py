# -*- coding: utf-8 -*-
{
    'name' : 'Card Decks Game',
    'version' : '16.0.0.0.1',
    "author": "Diogo Cordeiro",
    'summary': 'Playable Card Decks',
    'sequence': 10,
    'description': """
Playable Card Decks
===================
With this module you can configure decks of cards and play them

    """,
    'category': 'Services/Card Decks',
    'website': 'https://github.com/diogocsc/carddecks_game',
    'depends' : ["web", "carddecks"],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/game_template.xml',
        'views/deck_list_template.xml',
        'views/carddecks_game_menu.xml',
        'views/game.xml',
        'views/game_views.xml',
        'views/deck_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
    'assets': {
        'web.assets_backend': [
            "carddecks_game/static/src/css/styles.css",
            "carddecks_game/static/src/js/index.js",

        ],
        'web.assets_frontend': [
            "carddecks_game/static/src/css/styles.css",
            "carddecks_game/static/src/js/index.js",

        ],
    }
}
