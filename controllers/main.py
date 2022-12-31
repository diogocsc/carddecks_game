from odoo import http
from odoo.http import request


class Game(http.Controller):
    @http.route("/game")
    def game(self, **kwargs):
        Game = http.request.env["carddecks_game.game"]
        game = Game.search([("id", "=", kwargs.get("id"))])
        game.next_card_button()
        return http.request.render(
            "carddecks_game.game_template",
            {"game": game}
        )

    @http.route("/game/new")
    def play_game(self, **kwargs):
        deck_id = kwargs.get("deck_id")
        if not deck_id:
            return {'warning': {
                                'title': 'Warning!',
                                'message': 'Deck not specified'}}
        Game = http.request.env["carddecks_game.game"]
        game = Game.create({"deck": deck_id})
        return request.redirect('/game?id=%s' % game.id)

    @http.route("/decks")
    def deck_list(self, **kwargs):
        Deck = http.request.env["carddecks.deck"]
        decks = Deck.search([])
        return http.request.render(
            "carddecks_game.deck_list_template",
            {"decks": decks}
        )


