from collections import defaultdict
from django.core.management.base import BaseCommand
from myapp.models import ClauseRule

class Command(BaseCommand):
    help = ("Merges ClauseRule rows whose clause_type differs only by case "
            "or surrounding whitespace (e.g. 'Payment Terms' and "
            "'payment terms'), keeping the earliest-created row's casing.")

    def handle(self, *args, **options):

        groups = defaultdict(list)

        for rule in ClauseRule.objects.all().order_by("id"):
            key = rule.clause_type.strip().lower()
            groups[key].append(rule)

        merged = 0

        for key, rules in groups.items():

            if len(rules) <= 1:
                continue

            canonical = rules[0]
            duplicates = rules[1:]

            self.stdout.write(
                f"Merging {len(duplicates)} duplicate(s) of "
                f"'{canonical.clause_type}' into rule #{canonical.id}"
            )

            for dup in duplicates:
                dup.delete()
                merged += 1

        self.stdout.write(self.style.SUCCESS(f"Merged {merged} duplicate rule(s)."))
