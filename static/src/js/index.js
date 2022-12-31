/** @odoo-module **/


odoo.define('carddecks.deck', function (require) {
"use strict";

    window.play = play;
    function play(deck_id){
        this._rpc({
            model: 'carddecks_deck',
            method: 'create_game',
            args: [{"deck_id": deck_id}]

            }).then(function (result) {
                location.replace("/game?id="+result)
        });
    };
})