/**
 * Game Translation JavaScript
 * Handles dynamic translation of game content based on selected language
 */

odoo.define('carddecks_game.game_translation', function (require) {
    'use strict';

    var core = require('web.core');
    var rpc = require('web.rpc');

    var _t = core._t;

    var GameTranslation = {

        /**
         * Initialize game translation functionality
         */
        init: function() {
            this.bindLanguageChange();
            this.setupTranslations();
        },

        /**
         * Bind to language change events
         */
        bindLanguageChange: function() {
            var self = this;
            
            // Listen for language selector changes
            $(document).on('click', 'a[href*="/website/lang/"]', function(e) {
                var langHref = $(this).attr('href');
                if (langHref) {
                    var langCode = self.extractLanguageFromUrl(langHref);
                    setTimeout(function() {
                        self.translateGame(langCode);
                    }, 1000); // Wait for page reload/redirect
                }
            });

            // Listen for manual language change events
            $(document).on('change', 'select[name="lang"]', function() {
                var selectedLang = $(this).val();
                self.translateGame(selectedLang);
            });
        },

        /**
         * Setup initial translations based on current language
         */
        setupTranslations: function() {
            var self = this;
            
            // Detect current language from URL or body classes
            var currentLang = this.detectCurrentLanguage();
            if (currentLang && currentLang !== 'en') {
                this.translateGame(currentLang);
            }
        },

        /**
         * Extract language code from URL
         */
        extractLanguageFromUrl: function(url) {
            var match = url.match(/\/website\/lang\/([^\/]+)/);
            return match ? match[1] : 'en';
        },

        /**
         * Detect current language from page elements
         */
        detectCurrentLanguage: function() {
            // Check body classes first
            var bodyClassMatch = $('body').attr('class').match(/language-([a-z]{2})/);
            if (bodyClassMatch) {
                return bodyClassMatch[1];
            }

            // Check URL path
            var pathMatch = window.location.pathname.match(/\/([a-z]{2})\//);
            if (pathMatch) {
                return pathMatch[1];
            }

            // Check html lang attribute
            var htmlLang = $('html').attr('lang');
            if (htmlLang) {
                return htmlLang.split('_')[0];
            }

            return 'en';
        },

        /**
         * Translate game content
         */
        translateGame: function(langCode) {
            var self = this;
            
            if (langCode === 'en') {
                self.revertToOriginal();
                return;
            }

            // Show loading indicator
            this.showTranslationLoader();

            // Extract game ID from URL
            var gameId = this.extractGameIdFromUrl();
            if (!gameId) {
                console.warn('Could not extract game ID from URL');
                this.hideTranslationLoader();
                return;
            }

            // Make AJAX call to translate game
            $.ajax({
                url: '/game/translate',
                type: 'POST',
                data: JSON.stringify({
                    lang_code: langCode,
                    game_id: gameId
                }),
                contentType: 'application/json',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).done(function(result) {
                if (result.success) {
                    self.applyTranslations(result.game);
                } else {
                    console.warn('Translation failed:', result.error);
                }
                self.hideTranslationLoader();
            }).fail(function(error) {
                console.error('Translation error:', error);
                self.hideTranslationLoader();
            });
        },

        /**
         * Extract game ID from URL
         */
        extractGameIdFromUrl: function() {
            var urlParams = new URLSearchParams(window.location.search);
            var gameId = urlParams.get('id');
            if (gameId) {
                // Decode base64 to get actual game ID
                try {
                    var decoded = atob(gameId);
                    // Try to find game by name
                    return decoded;
                } catch (e) {
                    console.warn('Could not decode game ID:', e);
                }
            }
            return null;
        },

        /**
         * Apply translations to game elements
         */
        applyTranslations: function(translatedGame) {
            var self = this;
            
            // Update deck name
            if (translatedGame.deck_name) {
                $('.deck-name').text(translatedGame.deck_name);
            }
            
            // Update card text
            if (translatedGame.card_text) {
                $('.card h2').text(translatedGame.card_text);
                $('.card_subtitle h2').text(translatedGame.card_text);
            }
            
            // Update button texts
            if (translatedGame.next_card_text) {
                $('.card-button').filter(function() {
                    return $(this).text().trim() === 'Next Card';
                }).text(translatedGame.next_card_text);
            }
            
            if (translatedGame.start_game_text) {
                $('.card-button').filter(function() {
                    return $(this).text().trim() === 'Start Game';
                }).text(translatedGame.start_game_text);
            }
            
            if (translatedGame.new_game_text) {
                $('.card-button').filter(function() {
                    return $(this).text().trim() === 'New Game';
                }).text(translatedGame.new_game_text);
            }
            
            // Store original content for reversion
            this.storeOriginalContent();
        },

        /**
         * Store original content for reversion
         */
        storeOriginalContent: function() {
            $('.deck-name').each(function() {
                if (!$(this).data('original-text')) {
                    $(this).data('original-text', $(this).text());
                }
            });
            
            $('.card h2, .card_subtitle h2').each(function() {
                if (!$(this).data('original-text')) {
                    $(this).data('original-text', $(this).text());
                }
            });
            
            $('.card-button').each(function() {
                if (!$(this).data('original-text')) {
                    $(this).data('original-text', $(this).text());
                }
            });
        },

        /**
         * Revert to original language content
         */
        revertToOriginal: function() {
            $('.deck-name').each(function() {
                var originalText = $(this).data('original-text');
                if (originalText) {
                    $(this).text(originalText);
                }
            });
            
            $('.card h2, .card_subtitle h2').each(function() {
                var originalText = $(this).data('original-text');
                if (originalText) {
                    $(this).text(originalText);
                }
            });
            
            $('.card-button').each(function() {
                var originalText = $(this).data('original-text');
                if (originalText) {
                    $(this).text(originalText);
                }
            });
        },

        /**
         * Show translation loading indicator
         */
        showTranslationLoader: function() {
            var loader = '<div id="game-translation-loader" style="position: fixed; top: 20px; right: 20px; background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999;">Translating game...</div>';
            $('body').append(loader);
        },

        /**
         * Hide translation loading indicator
         */
        hideTranslationLoader: function() {
            $('#game-translation-loader').remove();
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        if ($('.card-game-container').length > 0) {
            GameTranslation.init();
        }
    });

    return GameTranslation;
});
