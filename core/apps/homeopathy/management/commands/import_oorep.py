from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

import psycopg2

from apps.homeopathy.models import (
    Repertory,
    RepertoryChapter,
    RepertoryRubric,
    RubricTranslation,
    RepertoryRemedy,
    RemedyRubric,
)


class Command(BaseCommand):
    help = "Import OOREP Publicum repertory into Sebagriho"

    BATCH_SIZE = 2000

    SOURCE_ABBREVIATION = "publicum"
    SOURCE_NAME = "OOREP Publicum"

    OOREP_DB = {
        "host": "oorep-db",
        "port": 5432,
        "dbname": "oorep_import",
        "user": "oorep",
        "password": "admin",
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting OOREP import..."))

        repertory = self.get_repertory()

        connection = psycopg2.connect(**self.OOREP_DB)

        try:
            self.import_chapters(connection, repertory)
            self.import_rubrics(connection, repertory)
            self.import_remedies(connection, repertory)
            self.import_remedy_rubrics(connection, repertory)
        finally:
            connection.close()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("OOREP import completed successfully."))

        self.print_summary(repertory)

    def get_repertory(self):
        repertory, created = Repertory.objects.get_or_create(
            slug="oorep-publicum",
            defaults={
                "name": self.SOURCE_NAME,
                "source": "OOREP",
                "version": "Publicum",
                "is_active": True,
            },
        )

        if not created:
            changed = False

            if repertory.name != self.SOURCE_NAME:
                repertory.name = self.SOURCE_NAME
                changed = True

            if repertory.source != "OOREP":
                repertory.source = "OOREP"
                changed = True

            if repertory.version != "Publicum":
                repertory.version = "Publicum"
                changed = True

            if not repertory.is_active:
                repertory.is_active = True
                changed = True

            if changed:
                repertory.save()

        self.stdout.write(f"Repertory: {repertory.name} ({repertory.pk})")

        return repertory

    # ------------------------------------------------------------------
    # Chapters
    # ------------------------------------------------------------------

    def import_chapters(self, connection, repertory):
        self.stdout.write("Importing chapters...")

        cursor = connection.cursor(name="oorep_chapters")

        cursor.execute(
            """
            SELECT
                chapterid,
                MIN(fullpath) AS chapter_name
            FROM public.rubric
            WHERE abbrev = %s
              AND chapterid >= 0
              AND fullpath IS NOT NULL
              AND fullpath NOT LIKE '%%,%%'
            GROUP BY chapterid
            ORDER BY chapterid
            """,
            [self.SOURCE_ABBREVIATION],
        )

        chapter_objects = []

        for source_id, name in cursor:
            if not name:
                continue

            chapter_objects.append(
                RepertoryChapter(
                    repertory=repertory,
                    source_id=source_id,
                    name=name.strip(),
                    slug=self.make_slug(name),
                )
            )

        cursor.close()

        if not chapter_objects:
            self.stdout.write("No chapters found.")
            return

        existing = {
            chapter.source_id: chapter
            for chapter in RepertoryChapter.objects.filter(repertory=repertory)
        }

        to_create = []
        to_update = []

        for chapter in chapter_objects:
            current = existing.get(chapter.source_id)

            if current:
                changed = False

                if current.name != chapter.name:
                    current.name = chapter.name
                    changed = True

                if current.slug != chapter.slug:
                    current.slug = chapter.slug
                    changed = True

                if changed:
                    to_update.append(current)
            else:
                to_create.append(chapter)

        if to_create:
            RepertoryChapter.objects.bulk_create(
                to_create,
                batch_size=self.BATCH_SIZE,
            )

        if to_update:
            RepertoryChapter.objects.bulk_update(
                to_update,
                ["name", "slug"],
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Chapters imported: {len(chapter_objects)}")
        )

    # ------------------------------------------------------------------
    # Rubrics
    # ------------------------------------------------------------------

    def import_rubrics(self, connection, repertory):
        self.stdout.write("Importing rubrics...")

        chapter_map = {
            chapter.source_id: chapter
            for chapter in RepertoryChapter.objects.filter(repertory=repertory)
        }

        # Existing rubrics.
        existing = {
            rubric.source_id: rubric
            for rubric in RepertoryRubric.objects.filter(repertory=repertory)
        }

        # First pass:
        # create/update rubric records without parent.
        cursor = connection.cursor(name="oorep_rubrics")

        cursor.execute(
            """
            SELECT
                id,
                chapterid,
                fullpath
            FROM public.rubric
            WHERE abbrev = %s
            ORDER BY id
            """,
            [self.SOURCE_ABBREVIATION],
        )

        created_count = 0
        updated_count = 0

        pending_create = []
        pending_update = []

        # We keep full_path -> source_id so parent relationships
        # can be reconstructed after all rubrics exist.
        path_to_source_id = {}

        for source_id, chapter_id, full_path in cursor:
            if not full_path:
                continue

            full_path = full_path.strip()

            parts = [part.strip() for part in full_path.split(",")]
            text = parts[-1]

            path_to_source_id[full_path] = source_id

            chapter = chapter_map.get(chapter_id)

            rubric = existing.get(source_id)

            if rubric:
                changed = False

                if rubric.text != text:
                    rubric.text = text
                    changed = True

                if rubric.full_path != full_path:
                    rubric.full_path = full_path
                    changed = True

                if rubric.chapter_id != (chapter.pk if chapter else None):
                    rubric.chapter = chapter
                    changed = True

                if rubric.source_abbreviation != self.SOURCE_ABBREVIATION:
                    rubric.source_abbreviation = self.SOURCE_ABBREVIATION
                    changed = True

                if changed:
                    pending_update.append(rubric)

                updated_count += 1

            else:
                pending_create.append(
                    RepertoryRubric(
                        repertory=repertory,
                        source_id=source_id,
                        chapter=chapter,
                        text=text,
                        full_path=full_path,
                        source_abbreviation=self.SOURCE_ABBREVIATION,
                    )
                )

                created_count += 1

            if len(pending_create) >= self.BATCH_SIZE:
                RepertoryRubric.objects.bulk_create(
                    pending_create,
                    batch_size=self.BATCH_SIZE,
                )
                pending_create.clear()

            if len(pending_update) >= self.BATCH_SIZE:
                RepertoryRubric.objects.bulk_update(
                    pending_update,
                    [
                        "chapter",
                        "text",
                        "full_path",
                        "source_abbreviation",
                    ],
                    batch_size=self.BATCH_SIZE,
                )
                pending_update.clear()

        cursor.close()

        if pending_create:
            RepertoryRubric.objects.bulk_create(
                pending_create,
                batch_size=self.BATCH_SIZE,
            )

        if pending_update:
            RepertoryRubric.objects.bulk_update(
                pending_update,
                [
                    "chapter",
                    "text",
                    "full_path",
                    "source_abbreviation",
                ],
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(f"Rubrics created: {created_count}")
        self.stdout.write(f"Rubrics updated: {updated_count}")

        # Refresh map after creation.
        rubric_map = {
            rubric.source_id: rubric
            for rubric in RepertoryRubric.objects.filter(repertory=repertory)
        }

        # --------------------------------------------------------------
        # Second pass: reconstruct parents from full_path.
        # --------------------------------------------------------------

        self.stdout.write("Building rubric hierarchy...")

        parent_updates = []

        for full_path, source_id in path_to_source_id.items():
            parts = [part.strip() for part in full_path.split(",")]

            if len(parts) <= 1:
                parent_id = None
            else:
                parent_path = ", ".join(parts[:-1])
                parent_source_id = path_to_source_id.get(parent_path)

                if parent_source_id is None:
                    parent_id = None
                else:
                    parent_id = rubric_map[parent_source_id].pk

            rubric = rubric_map[source_id]

            if rubric.parent_id != parent_id:
                rubric.parent_id = parent_id
                parent_updates.append(rubric)

            if len(parent_updates) >= self.BATCH_SIZE:
                RepertoryRubric.objects.bulk_update(
                    parent_updates,
                    ["parent"],
                    batch_size=self.BATCH_SIZE,
                )
                parent_updates.clear()

        if parent_updates:
            RepertoryRubric.objects.bulk_update(
                parent_updates,
                ["parent"],
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(self.style.SUCCESS("Rubric hierarchy completed."))

    # ------------------------------------------------------------------
    # Remedies
    # ------------------------------------------------------------------

    def import_remedies(self, connection, repertory):
        self.stdout.write("Importing remedies...")

        cursor = connection.cursor(name="oorep_remedies")

        cursor.execute("""
            SELECT
                id,
                nameabbrev,
                namelong,
                namealt
            FROM public.remedy
            ORDER BY id
            """)

        existing = {
            remedy.source_id: remedy
            for remedy in RepertoryRemedy.objects.filter(repertory=repertory)
        }

        pending_create = []
        pending_update = []

        created_count = 0
        updated_count = 0

        for source_id, abbreviation, name, alternative_name in cursor:
            abbreviation = (abbreviation or "").strip()
            name = (name or "").strip()
            if isinstance(alternative_name, list):
                alternative_name = ", ".join(
                    str(item).strip() for item in alternative_name if item
                )
            else:
                alternative_name = (alternative_name or "").strip()

            remedy = existing.get(source_id)

            if remedy:
                changed = False

                if remedy.abbreviation != abbreviation:
                    remedy.abbreviation = abbreviation
                    changed = True

                if remedy.name != name:
                    remedy.name = name
                    changed = True

                if remedy.alternative_name != alternative_name:
                    remedy.alternative_name = alternative_name
                    changed = True

                if changed:
                    pending_update.append(remedy)

                updated_count += 1

            else:
                pending_create.append(
                    RepertoryRemedy(
                        repertory=repertory,
                        source_id=source_id,
                        abbreviation=abbreviation,
                        name=name,
                        alternative_name=alternative_name,
                    )
                )

                created_count += 1

            if len(pending_create) >= self.BATCH_SIZE:
                RepertoryRemedy.objects.bulk_create(
                    pending_create,
                    batch_size=self.BATCH_SIZE,
                )
                pending_create.clear()

            if len(pending_update) >= self.BATCH_SIZE:
                RepertoryRemedy.objects.bulk_update(
                    pending_update,
                    [
                        "abbreviation",
                        "name",
                        "alternative_name",
                    ],
                    batch_size=self.BATCH_SIZE,
                )
                pending_update.clear()

        cursor.close()

        if pending_create:
            RepertoryRemedy.objects.bulk_create(
                pending_create,
                batch_size=self.BATCH_SIZE,
            )

        if pending_update:
            RepertoryRemedy.objects.bulk_update(
                pending_update,
                [
                    "abbreviation",
                    "name",
                    "alternative_name",
                ],
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Remedies created: {created_count}, " f"updated: {updated_count}"
            )
        )

    # ------------------------------------------------------------------
    # Rubric -> Remedy relationships
    # ------------------------------------------------------------------

    def import_remedy_rubrics(self, connection, repertory):
        self.stdout.write("Importing rubric/remedy relationships...")

        rubric_map = {
            rubric.source_id: rubric
            for rubric in RepertoryRubric.objects.filter(repertory=repertory)
        }

        remedy_map = {
            remedy.source_id: remedy
            for remedy in RepertoryRemedy.objects.filter(repertory=repertory)
        }

        # Existing relationships.
        existing = {
            (relation.rubric_id, relation.remedy_id): relation
            for relation in RemedyRubric.objects.filter(rubric__repertory=repertory)
        }

        cursor = connection.cursor(name="oorep_relations")

        cursor.execute(
            """
            SELECT
                rubricid,
                remedyid,
                weight
            FROM public.rubricremedy
            WHERE abbrev = %s
            ORDER BY rubricid, remedyid
            """,
            [self.SOURCE_ABBREVIATION],
        )

        pending_create = []
        pending_update = []

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for rubric_source_id, remedy_source_id, weight in cursor:
            rubric = rubric_map.get(rubric_source_id)
            remedy = remedy_map.get(remedy_source_id)

            if rubric is None or remedy is None:
                skipped_count += 1
                continue

            key = (rubric.pk, remedy.pk)

            relation = existing.get(key)

            if relation:
                if relation.grade != weight:
                    relation.grade = weight
                    pending_update.append(relation)

                updated_count += 1

            else:
                pending_create.append(
                    RemedyRubric(
                        rubric=rubric,
                        remedy=remedy,
                        grade=weight,
                    )
                )

                created_count += 1

            if len(pending_create) >= self.BATCH_SIZE:
                RemedyRubric.objects.bulk_create(
                    pending_create,
                    batch_size=self.BATCH_SIZE,
                    ignore_conflicts=True,
                )
                pending_create.clear()

            if len(pending_update) >= self.BATCH_SIZE:
                RemedyRubric.objects.bulk_update(
                    pending_update,
                    ["grade"],
                    batch_size=self.BATCH_SIZE,
                )
                pending_update.clear()

        cursor.close()

        if pending_create:
            RemedyRubric.objects.bulk_create(
                pending_create,
                batch_size=self.BATCH_SIZE,
                ignore_conflicts=True,
            )

        if pending_update:
            RemedyRubric.objects.bulk_update(
                pending_update,
                ["grade"],
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(self.style.SUCCESS(f"Relationships created: {created_count}"))

        self.stdout.write(f"Relationships updated: {updated_count}")

        if skipped_count:
            self.stdout.write(
                self.style.WARNING(f"Relationships skipped: {skipped_count}")
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_slug(value):
        import re
        from unicodedata import normalize

        value = normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    def print_summary(self, repertory):
        self.stdout.write("")
        self.stdout.write("========== IMPORT SUMMARY ==========")

        self.stdout.write(f"Repertory: {repertory.name}")

        self.stdout.write(
            f"Chapters: "
            f"{RepertoryChapter.objects.filter(repertory=repertory).count()}"
        )

        self.stdout.write(
            f"Rubrics: "
            f"{RepertoryRubric.objects.filter(repertory=repertory).count()}"
        )

        self.stdout.write(
            f"Remedies: "
            f"{RepertoryRemedy.objects.filter(repertory=repertory).count()}"
        )

        self.stdout.write(
            f"Relationships: {RemedyRubric.objects.filter(rubric__repertory=repertory).count()}"
        )

        self.stdout.write("====================================")
