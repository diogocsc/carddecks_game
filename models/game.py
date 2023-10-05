# -*- coding: utf-8 -*-
import random

from odoo import fields, models, api,_
import base64

class Game(models.Model):
    _name = "carddecks_game.game"
    _description = "Game"
    usedCards = fields.Many2many("carddecks.card", string="Played Cards")
    currentCard = fields.Many2one("carddecks.card", "Current Card")
    currentCard_cardText = fields.Char("Current Card text", related="currentCard.cardText")
    currentCard_image = fields.Binary("Current Image", related="currentCard.image")
    deck = fields.Many2one("carddecks.deck", "Game Deck")
    name = fields.Char(string='Game Number', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    _sql_constraints = [('unique_id', 'UNIQUE(name)', "Game Name must be unique"), ]
    base64_name = fields.Char(compute="_compute_base64_name", store=True)
    has_game_ended = fields.Boolean()


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('game_seq') or _('New')
        res = super().create(vals)
        return res

    @api.depends("name")
    def _compute_base64_name(self):
        for game in self:
            sample_string_bytes = game.name.encode("ascii")
            base64_bytes = base64.b64encode(sample_string_bytes)
            game.base64_name = base64_bytes.decode("ascii")

    def next_card_button(self):
        self.ensure_one()
        Card = self.env["carddecks.card"]
        playable_cards = Card.search([("deck.id", "=", self.deck.id),
                                      ("cardText", "not in", self.usedCards.mapped("cardText"))])
        self.currentCard = random.choice(playable_cards) if playable_cards else None
        self.has_game_ended = False if playable_cards else True
        if self.currentCard:
            self.usedCards += self.currentCard

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }