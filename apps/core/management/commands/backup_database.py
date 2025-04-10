import os
import time
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger('gitako.backup')

class Command(BaseCommand):
    help = 'Backup the database and upload to S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-to-s3',
            action='store_true',
            dest='upload_to_s3',
            help='Upload the backup to S3',
        )

    def handle(self, *args, **options):
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate timestamp for the backup file
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        
        # Get database settings
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            # PostgreSQL backup
            backup_file = os.path.join(backup_dir, f'backup-{timestamp}.sql')
            
            # Build the pg_dump command
            cmd = [
                'pg_dump',
                '-h', db_settings.get('HOST', 'localhost'),
                '-p', str(db_settings.get('PORT', '5432')),
                '-U', db_settings.get('USER', 'postgres'),
                '-d', db_name,
                '-f', backup_file,
                '--format=c'  # Custom format (compressed)
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings.get('PASSWORD', '')
            
            self.stdout.write(f'Creating PostgreSQL backup: {backup_file}')
            
            try:
                # Run the pg_dump command
                subprocess.run(cmd, env=env, check=True)
                self.stdout.write(self.style.SUCCESS(f'Successfully created backup: {backup_file}'))
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
                logger.error(f'Database backup failed: {str(e)}')
                return
        
        elif db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            # SQLite backup
            backup_file = os.path.join(backup_dir, f'backup-{timestamp}.sqlite3')
            
            self.stdout.write(f'Creating SQLite backup: {backup_file}')
            
            try:
                # Simply copy the SQLite file
                with open(db_settings['NAME'], 'rb') as src, open(backup_file, 'wb') as dst:
                    dst.write(src.read())
                self.stdout.write(self.style.SUCCESS(f'Successfully created backup: {backup_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
                logger.error(f'Database backup failed: {str(e)}')
                return
        
        else:
            self.stdout.write(self.style.ERROR(f'Unsupported database engine: {db_settings["ENGINE"]}'))
            return
        
        # Upload to S3 if requested
        if options['upload_to_s3']:
            self.upload_to_s3(backup_file, timestamp)
    
    def upload_to_s3(self, file_path, timestamp):
        """Upload the backup file to S3"""
        try:
            # Get S3 settings from environment
            bucket_name = os.environ.get('AWS_BACKUP_BUCKET_NAME')
            if not bucket_name:
                self.stdout.write(self.style.ERROR('AWS_BACKUP_BUCKET_NAME not set'))
                return
            
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            
            # Upload file
            file_name = os.path.basename(file_path)
            s3_path = f'database-backups/{timestamp}/{file_name}'
            
            self.stdout.write(f'Uploading backup to S3: {s3_path}')
            
            s3_client.upload_file(file_path, bucket_name, s3_path)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully uploaded backup to S3: s3://{bucket_name}/{s3_path}'))
            
            # Log the successful upload
            logger.info(f'Database backup uploaded to S3: s3://{bucket_name}/{s3_path}')
            
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'S3 upload failed: {str(e)}'))
            logger.error(f'S3 upload failed: {str(e)}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error during S3 upload: {str(e)}'))
            logger.error(f'Unexpected error during S3 upload: {str(e)}')