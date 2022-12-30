# -*- coding: utf-8 -*-
import random

from odoo import fields, models, api


class Game(models.Model):
    _name = "carddecks_game.game"
    _description = "Game"
    usedCards = fields.Many2many("carddecks.card", string="Played Cards")
    currentCard = fields.Many2one("carddecks.card", "Current Card")
    currentCard_cardText = fields.Char("Current Card text", related="currentCard.cardText")
    currentCard_image = fields.Binary("Current Image", related="currentCard.image")
    deck = fields.Many2one("carddecks.deck", "Game Deck")

    def next_card_button(self):
        self.ensure_one()
        Card = self.env["carddecks.card"]
        playable_cards = Card.search([("deck.id", "=", self.deck.id),
                                      ("cardText", "not in", self.usedCards.mapped("cardText"))])
        self.currentCard = random.choice(playable_cards) if playable_cards else None
        if self.currentCard:
            self.usedCards += self.currentCard

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }