import json
import re
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Prefetch

import requests

from apps.homeopathy.models import (
    Repertory,
    RepertoryChapter,
    RepertoryRubric,
    ChapterTranslation,
    RubricTranslation,
)

LANGUAGE_NAMES = {
    "bn": "Bangla (Bengali)",
}

# deep-translator's MyMemoryTranslator needs full locale-style codes, not
# plain ISO 639-1 codes (e.g. "bn" -> "bn-IN"). Extend this as more target
# languages are added.
MYMEMORY_LANGUAGE_CODES = {
    "bn": "bn-IN",
}
MYMEMORY_SOURCE_CODE = "en-GB"

MYMEMORY_QUOTA_MARKERS = (
    "MYMEMORY WARNING",
    "QUERY LENGTH LIMIT EXCEEDED",
    "YOU USED ALL AVAILABLE FREE TRANSLATIONS",
)


class Command(BaseCommand):
    help = (
        "Batch-translate repertory chapter names and rubric text into another "
        "language (default: Bangla), and store the results in "
        "ChapterTranslation / RubricTranslation. Translation happens once "
        "here; API endpoints only ever read the stored translations. "
        "Supports two free providers (MyMemory, unofficial Google Translate) "
        "and a paid provider (Anthropic API)."
    )

    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION = "2023-06-01"

    def add_arguments(self, parser):
        parser.add_argument(
            "--repertory",
            default="oorep-publicum",
            help="Repertory slug to translate.",
        )
        parser.add_argument(
            "--language",
            default="bn",
            help="Target language code to store translations under.",
        )
        parser.add_argument(
            "--provider",
            choices=["mymemory", "google", "anthropic"],
            default="mymemory",
            help=(
                "Translation backend. 'mymemory' and 'google' are free, no "
                "API key needed. 'anthropic' needs ANTHROPIC_API_KEY and API "
                "credit. If one free provider is blocked/rate-limited from "
                "your server, try the other."
            ),
        )
        parser.add_argument(
            "--email",
            default=None,
            help=(
                "Your email (--provider mymemory only). Raises MyMemory's "
                "free daily quota from 5,000 to 50,000 words. Optional."
            ),
        )
        parser.add_argument(
            "--model",
            default="claude-haiku-4-5-20251001",
            help="Anthropic model id to use for translation (--provider anthropic only).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="How many distinct terms to send per Anthropic API call (--provider anthropic only).",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.3,
            help="Seconds to sleep between requests (--provider mymemory/google only), to avoid rate limits.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of distinct terms translated (for a test run).",
        )
        parser.add_argument(
            "--only",
            choices=["chapters", "rubrics", "paths", "all"],
            default="all",
            help="Restrict which step(s) to run.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-translate terms that already have a stored translation.",
        )

    def handle(self, *args, **options):
        self.provider = options["provider"]
        self.model = options["model"]
        self.language = options["language"]
        self.batch_size = options["batch_size"]
        self.delay = options["delay"]
        self.limit = options["limit"]
        self.force = options["force"]

        if self.provider == "anthropic":
            api_key = getattr(settings, "ANTHROPIC_API_KEY", "")

            if not api_key:
                raise CommandError(
                    "ANTHROPIC_API_KEY is not configured. Add it to your .env file."
                )

            self.api_key = api_key
        elif self.provider == "mymemory":
            try:
                from deep_translator import MyMemoryTranslator
            except ImportError:
                raise CommandError(
                    "deep-translator is not installed. Run "
                    "`pip install deep-translator` (it's in requirements.txt)."
                )

            target_code = MYMEMORY_LANGUAGE_CODES.get(self.language)

            if not target_code:
                raise CommandError(
                    f"No MyMemory language code mapping for '{self.language}'. "
                    "Add it to MYMEMORY_LANGUAGE_CODES."
                )

            kwargs = {}

            if options.get("email"):
                kwargs["email"] = options["email"]

            self.free_translator = MyMemoryTranslator(
                source=MYMEMORY_SOURCE_CODE, target=target_code, **kwargs
            )
        else:
            try:
                from deep_translator import GoogleTranslator
            except ImportError:
                raise CommandError(
                    "deep-translator is not installed. Run "
                    "`pip install deep-translator` (it's in requirements.txt)."
                )

            self.free_translator = GoogleTranslator(
                source="en", target=self.language
            )

        try:
            repertory = Repertory.objects.get(slug=options["repertory"])
        except Repertory.DoesNotExist:
            raise CommandError(f"Repertory '{options['repertory']}' not found.")

        only = options["only"]

        if only in ("chapters", "all"):
            self.translate_chapters(repertory)

        if only in ("rubrics", "all"):
            self.translate_rubric_texts(repertory)

        if only in ("paths", "all"):
            self.build_rubric_full_paths(repertory)

        self.stdout.write(self.style.SUCCESS("Translation completed."))

    # ------------------------------------------------------------------
    # Chapters
    # ------------------------------------------------------------------

    def translate_chapters(self, repertory):
        self.stdout.write("Translating chapters...")

        queryset = RepertoryChapter.objects.filter(repertory=repertory)

        if not self.force:
            translated_ids = ChapterTranslation.objects.filter(
                chapter__repertory=repertory,
                language=self.language,
            ).values_list("chapter_id", flat=True)
            queryset = queryset.exclude(id__in=translated_ids)

        chapters = list(queryset.order_by("source_id"))

        if self.limit:
            chapters = chapters[: self.limit]

        if not chapters:
            self.stdout.write("No chapters need translation.")
            return

        distinct_names = sorted({chapter.name for chapter in chapters if chapter.name})

        self.stdout.write(f"Distinct chapter names to translate: {len(distinct_names)}")

        translation_map = self.translate_terms(distinct_names)

        existing = {
            ct.chapter_id: ct
            for ct in ChapterTranslation.objects.filter(
                chapter__in=chapters,
                language=self.language,
            )
        }

        to_create = []
        to_update = []

        for chapter in chapters:
            translated = translation_map.get(chapter.name)

            if not translated:
                continue

            current = existing.get(chapter.id)

            if current:
                current.name = translated
                to_update.append(current)
            else:
                to_create.append(
                    ChapterTranslation(
                        chapter=chapter,
                        language=self.language,
                        name=translated,
                    )
                )

        if to_create:
            ChapterTranslation.objects.bulk_create(to_create, batch_size=2000)

        if to_update:
            ChapterTranslation.objects.bulk_update(to_update, ["name"], batch_size=2000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Chapters translated: created {len(to_create)}, updated {len(to_update)}"
            )
        )

    # ------------------------------------------------------------------
    # Rubric text
    # ------------------------------------------------------------------

    def translate_rubric_texts(self, repertory):
        self.stdout.write("Translating rubric text...")

        queryset = RepertoryRubric.objects.filter(repertory=repertory)

        if not self.force:
            translated_ids = (
                RubricTranslation.objects.filter(
                    rubric__repertory=repertory,
                    language=self.language,
                )
                .exclude(text="")
                .values_list("rubric_id", flat=True)
            )
            queryset = queryset.exclude(id__in=translated_ids)

        rubrics = list(queryset.only("id", "text").order_by("source_id"))

        if self.limit:
            rubrics = rubrics[: self.limit]

        if not rubrics:
            self.stdout.write("No rubric text needs translation.")
            return

        distinct_texts = sorted({rubric.text for rubric in rubrics if rubric.text})

        self.stdout.write(f"Distinct rubric terms to translate: {len(distinct_texts)}")

        translation_map = self.translate_terms(distinct_texts)

        existing = {
            rt.rubric_id: rt
            for rt in RubricTranslation.objects.filter(
                rubric__in=rubrics,
                language=self.language,
            )
        }

        to_create = []
        to_update = []

        for rubric in rubrics:
            translated = translation_map.get(rubric.text)

            if not translated:
                continue

            current = existing.get(rubric.id)

            if current:
                current.text = translated
                to_update.append(current)
            else:
                to_create.append(
                    RubricTranslation(
                        rubric=rubric,
                        language=self.language,
                        text=translated,
                        full_path="",
                    )
                )

        if to_create:
            RubricTranslation.objects.bulk_create(to_create, batch_size=2000)

        if to_update:
            RubricTranslation.objects.bulk_update(to_update, ["text"], batch_size=2000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Rubric text translated: created {len(to_create)}, "
                f"updated {len(to_update)}"
            )
        )

    # ------------------------------------------------------------------
    # Rubric full paths (reconstructed from translated ancestor chain)
    # ------------------------------------------------------------------

    def build_rubric_full_paths(self, repertory):
        self.stdout.write("Building translated full paths...")

        rubrics = list(
            RepertoryRubric.objects.filter(repertory=repertory)
            .only("id", "parent_id", "text")
            .order_by("id")
        )
        rubric_map = {rubric.id: rubric for rubric in rubrics}

        translations = RubricTranslation.objects.filter(
            rubric__repertory=repertory,
            language=self.language,
        )
        translation_by_rubric = {t.rubric_id: t for t in translations}

        cache = {}

        def resolve_path(rubric_id):
            if rubric_id in cache:
                return cache[rubric_id]

            rubric = rubric_map.get(rubric_id)

            if rubric is None:
                return []

            translation = translation_by_rubric.get(rubric_id)
            own_text = translation.text if translation else rubric.text

            if rubric.parent_id:
                path = resolve_path(rubric.parent_id) + [own_text]
            else:
                path = [own_text]

            cache[rubric_id] = path

            return path

        to_update = []
        updated_count = 0

        for rubric in rubrics:
            translation = translation_by_rubric.get(rubric.id)

            if translation is None:
                continue

            full_path = ", ".join(resolve_path(rubric.id))

            if translation.full_path != full_path:
                translation.full_path = full_path
                to_update.append(translation)
                updated_count += 1

            if len(to_update) >= 2000:
                RubricTranslation.objects.bulk_update(
                    to_update, ["full_path"], batch_size=2000
                )
                to_update.clear()

        if to_update:
            RubricTranslation.objects.bulk_update(
                to_update, ["full_path"], batch_size=2000
            )

        self.stdout.write(
            self.style.SUCCESS(f"Full paths built/updated: {updated_count}")
        )

    # ------------------------------------------------------------------
    # Anthropic API helpers
    # ------------------------------------------------------------------

    def translate_terms(self, terms):
        """Translate a list of distinct English terms into self.language.

        Returns a dict {english_term: translated_term}. Identical terms are
        only ever translated once. Terms that fail to translate are left out
        of the result, so they get retried automatically on the next run.
        """
        if self.provider in ("mymemory", "google"):
            return self.translate_terms_free(terms)

        return self.translate_terms_anthropic(terms)

    # ------------------------------------------------------------------
    # Free providers: MyMemory / unofficial Google Translate
    # (both via deep-translator, called one term at a time)
    # ------------------------------------------------------------------

    def translate_terms_free(self, terms):
        result = {}
        total = len(terms)

        for index, term in enumerate(terms, start=1):
            translated = self.translate_single_free(term)

            if translated:
                result[term] = translated

            if self.delay:
                time.sleep(self.delay)

            if index % 25 == 0 or index == total:
                self.stdout.write(f"Translated {index}/{total} terms")

        return result

    def translate_single_free(self, term, retries=5):
        backoff = 5

        for attempt in range(retries):
            try:
                translated = self.free_translator.translate(term)

                if translated and self.is_quota_exceeded(translated):
                    raise CommandError(
                        f"{self.provider} daily quota exceeded: {translated}"
                    )

                return translated
            except CommandError:
                raise
            except Exception as exc:
                is_rate_limit = "TooManyRequests" in type(exc).__name__

                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to translate '{term}' (attempt {attempt + 1}/{retries}): {exc}"
                    )
                )

                if attempt == retries - 1:
                    break

                time.sleep(backoff if is_rate_limit else 1)
                backoff = min(backoff * 2, 60)

        self.stdout.write(
            self.style.WARNING(f"Giving up on '{term}' for now; will retry next run.")
        )

        return None

    @staticmethod
    def is_quota_exceeded(translated_text):
        upper = translated_text.upper()
        return any(marker in upper for marker in MYMEMORY_QUOTA_MARKERS)

    # ------------------------------------------------------------------
    # Paid provider: Anthropic API
    # ------------------------------------------------------------------

    def translate_terms_anthropic(self, terms):
        result = {}
        total = len(terms)

        for offset in range(0, total, self.batch_size):
            batch = terms[offset : offset + self.batch_size]

            translated_batch = self.call_claude_batch(batch)

            if len(translated_batch) != len(batch):
                self.stdout.write(
                    self.style.WARNING(
                        f"Batch size mismatch at offset {offset}: expected "
                        f"{len(batch)}, got {len(translated_batch)}. Skipping "
                        "this batch."
                    )
                )
                continue

            for source, translated in zip(batch, translated_batch):
                if translated:
                    result[source] = translated

            done = min(offset + self.batch_size, total)
            self.stdout.write(f"Translated {done}/{total} terms")

        return result

    def call_claude_batch(self, batch, retries=3):
        numbered = "\n".join(f"{idx + 1}. {term}" for idx, term in enumerate(batch))
        language_name = LANGUAGE_NAMES.get(self.language, self.language)

        prompt = (
            "You are translating terms from a homeopathic repertory (a medical "
            "symptom index) from English into "
            f"{language_name}. These are short clinical/symptom phrases (body "
            "parts, sensations, modalities like '> warmth' meaning 'better "
            "from warmth', or '<' meaning 'worse from'). Keep any leading '>' "
            "or '<' symbol in front of the translation. Preserve proper nouns "
            "or Latin remedy abbreviations as-is if present. Translate "
            f"naturally, the way a {language_name}-speaking homeopathic "
            "practitioner would write it, not word-for-word.\n\n"
            f"Translate each numbered English term below into {language_name}. "
            "Respond with ONLY a JSON array of strings, in the same order and "
            "same length as the input, with no extra commentary.\n\n"
            f"{numbered}"
        )

        last_error = None

        for attempt in range(retries):
            try:
                response = requests.post(
                    self.ANTHROPIC_API_URL,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": self.ANTHROPIC_VERSION,
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 4096,
                        "temperature": 0,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60,
                )
                if not response.ok:
                    raise CommandError(
                        f"{response.status_code} {response.reason} from Anthropic API: "
                        f"{response.text}"
                    )
                data = response.json()
                content = data["content"][0]["text"]
                return self.parse_json_array(content)
            except CommandError as exc:
                last_error = exc
                self.stdout.write(
                    self.style.WARNING(
                        f"Translation batch failed (attempt {attempt + 1}/{retries}): {exc}"
                    )
                )
                time.sleep(2 * (attempt + 1))
            except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
                last_error = exc
                self.stdout.write(
                    self.style.WARNING(
                        f"Translation batch failed (attempt {attempt + 1}/{retries}): {exc}"
                    )
                )
                time.sleep(2 * (attempt + 1))

        raise CommandError(f"Failed to translate batch after {retries} retries: {last_error}")

    @staticmethod
    def parse_json_array(content):
        content = content.strip()
        content = re.sub(r"^```(json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
        return json.loads(content)
