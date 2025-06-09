import logging
import time  # Added for the delay
from django.core.management.base import BaseCommand
from django.core.management import call_command

# These are the OpenKamer modules that contain the scraping logic
import openkamer.parliament
import openkamer.kamervraag
import openkamer.dossier
import stats.models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Scrapes OpenKamer data for a specified range of years,
    with added resilience to prevent stopping on errors.

    Example usage:
    python manage.py scrape_range --start-year 2010 --end-year 2024
    """

    def add_arguments(self, parser):
        # Required arguments for the year range
        parser.add_argument(
            '--start-year',
            type=int,
            required=True,
            help='The first year of the range to scrape data for (inclusive).'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            required=True,
            help='The last year of the range to scrape data for (inclusive).'
        )
        # Optional argument from the original script
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=False,
            help='Do not create items that already exist.'
        )

    def handle(self, *args, **options):
        start_year = options['start_year']
        end_year = options['end_year']
        skip_existing = options['skip_existing']

        self.stdout.write(f"Starting data scrape for years: {start_year}-{end_year}")

        # Step 1: Create the foundational parliament and government data (runs once)
        self.stdout.write("Scraping parliament and government base data...")
        openkamer.parliament.create_parliament_and_government()
        self.stdout.write(self.style.SUCCESS("✓ Parliament and government complete."))

        # Step 2: Scrape law proposals (Dossiers)
        self.stdout.write("Scraping all law proposals (dossiers)...")
        failed_dossiers = openkamer.dossier.create_wetsvoorstellen_all(skip_existing)
        if failed_dossiers:
            logger.error('The following dossiers failed to scrape: ' + str(failed_dossiers))
        self.stdout.write(self.style.SUCCESS("✓ Law proposals complete."))

        # Step 3: Loop through the specified years and scrape parliamentary questions (Kamervragen)
        self.stdout.write("Scraping parliamentary questions (Kamervragen) by year...")
        for year in range(start_year, end_year + 1):
            try:  # Start of the error handling block
                self.stdout.write(f"  Scraping questions for {year}...")
                openkamer.kamervraag.create_kamervragen(year=year, skip_existing=skip_existing)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Finished {year}"))

            except Exception as e:  # Catch any possible error during the year's scrape
                # If anything goes wrong, print the error and continue to the next year
                self.stderr.write(self.style.ERROR(f"  ✗ FAILED to scrape questions for {year}. Error: {e}"))
                self.stderr.write(self.style.ERROR("    Continuing to the next year..."))
                continue  # This ensures the loop moves to the next year

            # It's good practice to add a small delay to avoid overwhelming the server (rate limiting)
            time.sleep(1)  # Sleep for 1 second between each year's scrape

        self.stdout.write(self.style.SUCCESS("✓ Parliamentary questions complete."))
        
        # Step 4: Update all statistics
        self.stdout.write("Updating all statistics...")
        stats.models.update_all()
        self.stdout.write(self.style.SUCCESS("✓ Statistics updated."))
        
        self.stdout.write(self.style.SUCCESS("\nScraping for the specified range is complete!"))