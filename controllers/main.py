from odoo import http
from odoo.http import request
import logging
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from googletrans import Translator
except ImportError:
    Translator = None

_logger = logging.getLogger(__name__)

# Simple in-memory cache for translations (cleared on server restart)
_translation_cache = {}


class Game(http.Controller):

    def _get_user_language(self):
        """Get current user's language code"""
        # Priority 1: Check URL path for language prefix (e.g., /pt/game)
        path_parts = request.httprequest.path.split('/')
        if len(path_parts) > 1 and len(path_parts[1]) == 2:
            lang_code = path_parts[1]
            _logger.info(f"Language from URL path: {lang_code}")
            return lang_code
        
        # Priority 2: Check frontend_lang cookie (set by Odoo website language selector)
        frontend_lang_cookie = request.httprequest.cookies.get('frontend_lang', None)
        if frontend_lang_cookie:
            lang_code = frontend_lang_cookie.split('_')[0] if '_' in frontend_lang_cookie else frontend_lang_cookie
            _logger.info(f"Language from frontend_lang cookie: {frontend_lang_cookie} -> {lang_code}")
            return lang_code
        
        # Priority 3: Check Odoo context language
        context_lang = request.env.context.get('lang', None)
        if context_lang:
            lang_code = context_lang.split('_')[0] if '_' in context_lang else context_lang
            _logger.info(f"Language from context: {context_lang} -> {lang_code}")
            return lang_code
        
        # Default: English
        _logger.info("No language detected, defaulting to English")
        return 'en'

    def _translate_text(self, text, target_lang):
        """Single text translation worker function with caching"""
        if not text or not text.strip():
            return text
        
        # Check cache first
        cache_key = f"{target_lang}:{text}"
        if cache_key in _translation_cache:
            return _translation_cache[cache_key]
        
        # Translate if not in cache
        try:
            translator = Translator()
            result = translator.translate(text, dest=target_lang)
            translated_text = result.text
            
            # Store in cache
            _translation_cache[cache_key] = translated_text
            
            # Limit cache size to 1000 entries to avoid memory issues
            if len(_translation_cache) > 1000:
                # Remove oldest 200 entries
                keys_to_remove = list(_translation_cache.keys())[:200]
                for key in keys_to_remove:
                    del _translation_cache[key]
            
            return translated_text
        except Exception:
            return text

    def _translate_game_content(self, game, target_lang):
        """Translate game content including card text and UI elements - FAST parallel version"""
        try:
            # Create a wrapper object that preserves the original game
            class GameWrapper:
                def __init__(self, original_game):
                    self._original_game = original_game
                    # Set default UI button texts (fallback to English)
                    self.next_card_text = "Next Card"
                    self.start_game_text = "Start Game"
                    self.new_game_text = "New Game"
                    
                def __getattr__(self, name):
                    # Delegate to original game for any attribute not explicitly set
                    return getattr(self._original_game, name)
            
            wrapped_game = GameWrapper(game)
            
            # Only translate if Translator is available and target language is not English
            if Translator and target_lang != 'en':
                _logger.info(f"Translating game content to {target_lang} (parallel mode)")
                
                # Prepare all translation tasks
                translation_tasks = []
                
                # Task 1: Deck name
                if game.deck and game.deck.name:
                    translation_tasks.append(('deck_name', game.deck.name))
                
                # Task 2: Card text
                if game.currentCard and game.currentCard.cardText:
                    translation_tasks.append(('card_text', game.currentCard.cardText))
                
                # Task 3-5: UI buttons
                translation_tasks.extend([
                    ('next_card', "Next Card"),
                    ('start_game', "Start Game"),
                    ('new_game', "New Game"),
                ])
                
                # Execute all translations in parallel using ThreadPoolExecutor
                translations = {}
                if translation_tasks:
                    with ThreadPoolExecutor(max_workers=min(5, len(translation_tasks))) as executor:
                        # Submit all translation tasks
                        future_to_task = {
                            executor.submit(self._translate_text, text, target_lang): task_type
                            for task_type, text in translation_tasks
                        }
                        
                        # Collect results as they complete
                        for future in as_completed(future_to_task):
                            task_type = future_to_task[future]
                            try:
                                translations[task_type] = future.result()
                            except Exception as e:
                                _logger.warning(f"Translation failed for {task_type}: {e}")
                                # Keep original text if translation fails
                                translations[task_type] = dict(translation_tasks).get(task_type, '')
                
                # Apply translations using wrappers
                
                # Deck wrapper
                if 'deck_name' in translations and game.deck:
                    class DeckWrapper:
                        def __init__(self, original_deck, translated_name):
                            self._original_deck = original_deck
                            self.name = translated_name
                        
                        def __getattr__(self, name):
                            return getattr(self._original_deck, name)
                    
                    wrapped_game.deck = DeckWrapper(game.deck, translations['deck_name'])
                    _logger.info(f"Deck: {game.deck.name} -> {translations['deck_name']}")
                
                # Card wrapper
                if 'card_text' in translations and game.currentCard:
                    class CardWrapper:
                        def __init__(self, original_card, translated_text):
                            self._original_card = original_card
                            self.cardText = translated_text
                        
                        def __getattr__(self, name):
                            return getattr(self._original_card, name)
                    
                    wrapped_game.currentCard = CardWrapper(game.currentCard, translations['card_text'])
                    _logger.info(f"Card: {len(game.currentCard.cardText)} chars translated")
                
                # Button translations
                wrapped_game.next_card_text = translations.get('next_card', "Next Card")
                wrapped_game.start_game_text = translations.get('start_game', "Start Game")
                wrapped_game.new_game_text = translations.get('new_game', "New Game")
                
                _logger.info(f"Buttons: {wrapped_game.next_card_text}, {wrapped_game.start_game_text}, {wrapped_game.new_game_text}")
            else:
                _logger.info(f"No translation needed: Translator={Translator is not None}, target_lang={target_lang}")
            
            return wrapped_game
            
        except Exception as e:
            _logger.error(f"Game translation failed: {str(e)}", exc_info=True)
            # Return original game with default button texts
            game.next_card_text = "Next Card"
            game.start_game_text = "Start Game"
            game.new_game_text = "New Game"
            return game

    @http.route("/game", auth="public")
    def game(self, **kwargs):
        Game = http.request.env["carddecks_game.game"]
        game = Game.sudo().search([("base64_name", "=", kwargs.get("id"))])
        if not kwargs.get("start"):
            game.next_card_button()
        
        # Get user's current language for translation
        user_lang = self._get_user_language()
        cookies = request.httprequest.cookies
        _logger.info(f"Game request - Detected language: {user_lang}, Path: {request.httprequest.path}, Context lang: {request.env.context.get('lang')}, Cookies: frontend_lang={cookies.get('frontend_lang', 'NOT SET')}")
        
        # Translate game content if not English and googletrans is available
        translated_game = self._translate_game_content(game, user_lang)
        
        return http.request.render(
            "carddecks_game.game_template",
            {"game": translated_game}
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
        return request.redirect('/game?id=%s&start=1' % game.base64_name)

    @http.route(['/game/translate'], type='json', auth='public', website=True)
    def translate_game(self, lang_code=None, game_id=None, **kwargs):
        """JSON endpoint to translate game content"""
        if not Translator:
            return {'error': 'googletrans library not available'}
        
        user_lang = lang_code or self._get_user_language()
        if user_lang == 'en':
            return {'message': 'No translation needed for English'}
        
        try:
            # Get game by ID or base64_name
            Game = request.env["carddecks_game.game"]
            if game_id:
                game = Game.sudo().browse(game_id)
            else:
                # Try to get from current session or context
                return {'error': 'Game ID required for translation'}
            
            if not game.exists():
                return {'error': 'Game not found'}
            
            # Translate game content
            translated_game = self._translate_game_content(game, user_lang)
            
            return {
                'success': True,
                'target_language': user_lang,
                'game': {
                    'deck_name': translated_game.deck.name if translated_game.deck else '',
                    'card_text': translated_game.currentCard.cardText if translated_game.currentCard else '',
                    'next_card_text': translated_game.next_card_text,
                    'start_game_text': translated_game.start_game_text,
                    'new_game_text': translated_game.new_game_text,
                }
            }
            
        except Exception as e:
            return {'error': f'Translation failed: {str(e)}'}

    # Disabled - now handled by subscription_plans module
    # @http.route("/decks", auth="public")
    # def deck_list(self, **kwargs):
    #     Deck = http.request.env["carddecks.deck"]
    #     decks = Deck.sudo().search([("is_public", "=", True)])
    #     return http.request.render(
    #         "carddecks_game.deck_list_template",
    #         {"decks": decks}
    #     )


