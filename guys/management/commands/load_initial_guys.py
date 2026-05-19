"""Команда для загрузки начальных данных в БД при первом запуске приложения"""
from django.conf import settings
from django.core.management.base import BaseCommand

from guys.models import Guy
from guys.services import RandomGuysAPIError, load_guys


class Command(BaseCommand):
    help = 'Load initial guys from the external randomdatatools API on server start.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=settings.INITIAL_LOAD_COUNT,
            help='How many guys to fetch (default: settings.INITIAL_LOAD_COUNT).',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Load even if the DB already has guys in it.',
        )

    def handle(self, *args, **options):
        count = options['count']
        force = options['force']

        existing = Guy.objects.count()
        if existing > 0 and not force:
            self.stdout.write(self.style.WARNING(
                f'DB already contains {existing} guys; skipping. Use --force to load anyway.'
            ))
            return

        self.stdout.write(f'Loading {count} guys from external API...')
        try:
            created = load_guys(count)
        except RandomGuysAPIError as exc:
            self.stderr.write(self.style.ERROR(f'Failed to load: {exc}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Loaded {created} guys.'))
