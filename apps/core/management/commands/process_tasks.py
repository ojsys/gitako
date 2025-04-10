from django.core.management.base import BaseCommand
from background_task.tasks import process_tasks
import time
import logging

logger = logging.getLogger('gitako')

class Command(BaseCommand):
    help = 'Process background tasks (alternative to Celery for cPanel)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=0,
            help='Duration in seconds to run the command (0 for single run)',
        )
        parser.add_argument(
            '--sleep',
            type=float,
            default=5.0,
            help='Sleep time between each check',
        )

    def handle(self, *args, **options):
        duration = options['duration']
        sleep_time = options['sleep']
        
        self.stdout.write(f"Starting background task processing")
        
        if duration > 0:
            self.stdout.write(f"Running for {duration} seconds")
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    process_tasks()
                    time.sleep(sleep_time)
                except Exception as e:
                    logger.error(f"Error processing tasks: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        else:
            self.stdout.write("Running once")
            try:
                process_tasks()
            except Exception as e:
                logger.error(f"Error processing tasks: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Task processing completed"))