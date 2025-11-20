from django.shortcuts import render
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Prefer googletrans (more reliable) if available, otherwise fall back to `translate` package
try:
    from googletrans import Translator as GoogleTranslator
    _google_available = True
except Exception:
    GoogleTranslator = None
    _google_available = False

try:
    from translate import Translator as TranslatePkgTranslator
    _translatepkg_available = True
except Exception:
    TranslatePkgTranslator = None
    _translatepkg_available = False


def home(request):
    translation = None
    text = ""
    selected_language = None

    # Provide available languages (list of (code, name)) to the template
    available_languages = getattr(settings, 'LANGUAGES', [])

    if request.method == "POST":
        text = request.POST.get("translate", "").strip()
        # the form posts the language *code* (e.g. 'hi', 'de')
        selected_language = request.POST.get("language")
        lang_code = selected_language or 'en'

        if not text:
            translation = "Please enter text to translate."
        else:
            # Try googletrans first
            if _google_available:
                try:
                    g = GoogleTranslator()
                    result = g.translate(text, dest=lang_code)
                    translation = getattr(result, 'text', str(result))
                except Exception as e:
                    logger.exception("googletrans failed, will try fallback: %s", e)
                    translation = None

            # Fallback to `translate` package if googletrans not available or failed
            if translation is None and _translatepkg_available:
                try:
                    t = TranslatePkgTranslator(to_lang=lang_code)
                    translation = t.translate(text)
                except Exception as e:
                    logger.exception("translate package failed: %s", e)
                    translation = f"Translation failed: {e}"

            if translation is None:
                translation = "Translation provider not available or failed."

    return render(request, "index.html", {
        'translation': translation,
        'text': text,
        'language': selected_language,
        'languages': available_languages,
    })