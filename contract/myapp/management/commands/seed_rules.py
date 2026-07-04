from django.core.management.base import BaseCommand
from myapp.models import ClauseRule

RULES = [
    {
        "clause_type": "Confidentiality",
        "keyword": "confidentiality, non-disclosure, nda, trade secret, confidential",
        "risk_level_if_missing": "high",
        "description": "Protects sensitive information shared between parties. "
                       "Crucial for protecting intellectual property and trade secrets.",
    },
    {
        "clause_type": "Payment Terms",
        "keyword": "payment, net 30, invoice, compensation, fees, remuneration, payable",
        "risk_level_if_missing": "high",
        "description": "Defines how and when payments are made, late fees, "
                       "and invoicing procedures.",
    },
    {
        "clause_type": "Termination",
        "keyword": "terminate, termination, end date, cancellation, expiration",
        "risk_level_if_missing": "high",
        "description": "Specifies how the contract can be ended by either party, "
                       "either for convenience or for cause.",
    },
    {
        "clause_type": "Liability",
        "keyword": "liability, limitation of liability, damages, cap, indirect damages",
        "risk_level_if_missing": "high",
        "description": "Limits the amount and types of damages a party can be "
                       "sued for if a breach occurs.",
    },
    {
        "clause_type": "Indemnification",
        "keyword": "indemnify, hold harmless, defend, indemnification, compensate",
        "risk_level_if_missing": "medium",
        "description": "One party agrees to compensate the other for certain harms, "
                       "losses, or legal costs arising from third-party claims.",
    },
    {
        "clause_type": "Dispute Resolution",
        "keyword": "arbitration, mediation, court, governing law, jurisdiction, venue",
        "risk_level_if_missing": "medium",
        "description": "Dictates how legal disputes will be resolved (e.g., arbitration "
                       "vs. litigation) and what state's laws apply.",
    },
    {
        "clause_type": "Force Majeure",
        "keyword": "force majeure, act of god, unforeseen, pandemic, natural disaster, strike",
        "risk_level_if_missing": "medium",
        "description": "Relieves parties from liability if unforeseeable, unavoidable "
                       "events prevent them from fulfilling their obligations.",
    },
    {
        "clause_type": "Intellectual Property",
        "keyword": "intellectual property, copyright, patent, trademark, ownership, license",
        "risk_level_if_missing": "high",
        "description": "Clarifies who owns the intellectual property created or used "
                       "during the performance of the contract.",
    },
    {
        "clause_type": "Warranty",
        "keyword": "warranty, represent, as is, merchantability, fitness for a particular purpose",
        "risk_level_if_missing": "low",
        "description": "Guarantees or assurances made by one party about the quality "
                       "or state of a product, service, or fact.",
    },
    {
        "clause_type": "Data Privacy",
        "keyword": "gdpr, ccpa, personal data, privacy policy, data protection, pi, pii",
        "risk_level_if_missing": "high",
        "description": "Requirements for handling personal information, especially "
                       "important when dealing with European or Californian citizens.",
    },
]

class Command(BaseCommand):
    help = "Seeds the standard set of clause rules used by the risk analysis engine."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing ClauseRule rows before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted_count, _ = ClauseRule.objects.all().delete()
            self.stdout.write(f"Deleted {deleted_count} existing rule(s).")

        created = 0
        updated = 0

        for rule_data in RULES:
            obj, was_created = ClauseRule.objects.update_or_create(
                clause_type=rule_data["clause_type"],
                defaults={
                    "keyword": rule_data["keyword"],
                    "risk_level_if_missing": rule_data["risk_level_if_missing"],
                    "description": rule_data["description"],
                    "is_active": True,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} rule(s) created, {updated} rule(s) updated."
            )
        )
