from odoo import http
from odoo.http import request


class Game(http.Controller):
    @http.route("/game", auth="public")
    def game(self, **kwargs):
        Game = http.request.env["carddecks_game.game"]
        game = Game.sudo().search([("base64_name", "=", kwargs.get("id"))])
        if not kwargs.get("start"):
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
        return request.redirect('/game?id=%s&start=1' % game.base64_name)

    @http.route("/game/special/new", auth="public")
    def play_game_2(self, **kwargs):
        """
        This was created following a specific prospect request,
        regarding having cards directed to language learning decks.
        """
        deck_name = kwargs.get("deck_name")
        if not deck_name:
            return {'warning': {
                                'title': 'Warning!',
                                'message': 'Deck not specified'}}
        Game = http.request.env["carddecks_game.game"]
        Deck = http.request.env["carddecks.deck"]
        deck_id = Deck.sudo().search([("name", "=", deck_name)], limit=1).id
        print(f"DECK ID :::: {deck_id}")
        game = Game.sudo().create({"deck": deck_id})
        return request.redirect('/game?id=%s' % game.base64_name)

    @http.route("/decks", auth="public")
    def deck_list(self, **kwargs):
        Deck = http.request.env["carddecks.deck"]
        decks = Deck.sudo().search([("is_public", "=", True)])
        return http.request.render(
            "carddecks_game.deck_list_template",
            {"decks": decks}
        )


