import os
import shutil
import logging
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('gitako.background')

class Command(BaseCommand):
    help = 'Rotate and archive logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to keep logs before archiving',
        )
        parser.add_argument(
            '--archive-dir',
            type=str,
            default=None,
            help='Directory to store archived logs',
        )

    def handle(self, *args, **options):
        days = options['days']
        archive_dir = options['archive_dir']
        
        if not archive_dir:
            archive_dir = os.path.join(settings.BASE_DIR, '../logs/archive')
        
        # Ensure archive directory exists
        os.makedirs(archive_dir, exist_ok=True)
        
        # Get log directory
        log_dir = os.path.join(settings.BASE_DIR, '../logs')
        
        # Current date for archive folder
        today = datetime.datetime.now().strftime('%Y%m%d')
        archive_subdir = os.path.join(archive_dir, today)
        os.makedirs(archive_subdir, exist_ok=True)
        
        self.stdout.write(f"Rotating logs older than {days} days to {archive_subdir}")
        
        # Get cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # Process log files
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            
            # Skip directories and non-log files
            if os.path.isdir(file_path) or not filename.endswith(('.log', '.json')):
                continue
            
            # Check file modification time
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_date:
                # Archive the file
                archive_path = os.path.join(archive_subdir, filename)
                self.stdout.write(f"Archiving {filename} to {archive_path}")
                
                try:
                    shutil.copy2(file_path, archive_path)
                    # Truncate the original file
                    open(file_path, 'w').close()
                    logger.info(f"Archived log file {filename} to {archive_path}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error archiving {filename}: {str(e)}"))
                    logger.error(f"Error archiving log file {filename}", exc_info=True)
        
        self.stdout.write(self.style.SUCCESS("Log rotation completed"))