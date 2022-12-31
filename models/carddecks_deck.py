# -*- coding: utf-8 -*-
from odoo import fields, models


class Deck(models.Model):
    _inherit = "carddecks.deck"

    def create_new_game(self):
        self.ensure_one()
        Game = self.env["carddecks_game.game"]
        game = Game.create({"deck": self.id})
        return {
            'name': 'Play Game',
            'type': 'ir.actions.act_window',
            'res_model': 'carddecks_game.game',
            'view_mode': 'form',
            'target': 'main',
            'res_id': game.id
        }

    def create_game(self, deck_id):
        self.ensure_one()
        Game = self.env["carddecks_game.game"]
        game = Game.create({"deck": deck_id})
        return game.id
