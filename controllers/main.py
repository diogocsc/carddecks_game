from odoo import http
from odoo.http import request


class Game(http.Controller):
    @http.route("/game", auth="public")
    def game(self, **kwargs):
        Game = http.request.env["carddecks_game.game"]
        game = Game.sudo().search([("base64_name", "=", kwargs.get("id"))])
        game.next_card_button()
        return http.request.render(
            "carddecks_game.game_template",
            {"game": game}
        )

    @http.route("/game/new", auth="public")
    def play_game(self, **kwargs):
        deck_id = kwargs.get("deck_id")
        if not deck_id:
            return {'warning': {
                                'title': 'Warning!',
                                'message': 'Deck not specified'}}
        Game = http.request.env["carddecks_game.game"]
        game = Game.sudo().create({"deck": deck_id})
        return request.redirect('/game?id=%s' % game.base64_name)

    @http.route("/decks", auth="public")
    def deck_list(self, **kwargs):
        Deck = http.request.env["carddecks.deck"]
        decks = Deck.sudo().search([])
        return http.request.render(
            "carddecks_game.deck_list_template",
            {"decks": decks}
        )


