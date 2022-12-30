from odoo import http
from odoo.http import request


class Game(http.Controller):
    @http.route("/game")
    def game(self, **kwargs):
        Game = http.request.env["carddecks_game.game"]
        game = Game.search([("id", "=", kwargs.get("id"))])
        return http.request.render(
            "carddecks_game.game_template",
            {"game": game}
        )

    @http.route("/decks")
    def deck_list(self, **kwargs):
        Deck = http.request.env["carddecks.deck"]
        decks = Deck.search([])
        return http.request.render(
            "carddecks_game.deck_list_template",
            {"decks": decks}
        )

    def play_game(self, **kwargs):
        Deck=self.env["carddecks.deck"]
        deck = Deck.search([("deck.name","=",kwargs.get("deck"))])
        Game = self.env["carddecks_game.game"]
        game = Game.create({"deck": deck.id})
        return request.redirect('/game?id=%s' % game.id)
