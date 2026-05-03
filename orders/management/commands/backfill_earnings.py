from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order, Earning


class Command(BaseCommand):
    help = "Backfill earnings for completed orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many earnings would be created without writing to DB.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        completed_orders = Order.objects.filter(status="Completed")
        created_count = 0
        updated_count = 0

        for order in completed_orders:
            completed_at = order.created_at
            defaults = {
                "date": completed_at.date(),
                "completed_at": completed_at,
                "amount": order.total_amount,
            }

            if dry_run:
                if not Earning.objects.filter(order=order).exists():
                    created_count += 1
                else:
                    updated_count += 1
                continue

            earning, created = Earning.objects.update_or_create(
                order=order,
                defaults=defaults,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would create {created_count} and update {updated_count} earnings."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {created_count} and updated {updated_count} earnings."
                )
            )
