#!/usr/bin/env python3
"""
Deployment script for Gitako on cPanel hosting.
This script handles the deployment process for cPanel environments.
"""
import os
import sys
import subprocess
import shutil
import argparse
from datetime import datetime

def run_command(command):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result.returncode == 0

def create_backup():
    """Create a backup of the current application"""
    backup_dir = os.path.expanduser("~/backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"gitako_backup_{timestamp}")
    
    print(f"Creating backup at {backup_path}")
    
    # Create app directory backup
    app_dir = os.path.expanduser("~/gitako")
    if os.path.exists(app_dir):
        shutil.copytree(app_dir, backup_path)
        print(f"Application backup created at {backup_path}")
    else:
        print("No existing application to backup")
    
    # Backup database
    db_backup_file = os.path.join(backup_dir, f"gitako_db_backup_{timestamp}.sql")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    
    if db_name and db_user and db_password:
        backup_cmd = f"mysqldump -u {db_user} -p'{db_password}' {db_name} > {db_backup_file}"
        if run_command(backup_cmd):
            print(f"Database backup created at {db_backup_file}")
        else:
            print("Database backup failed")
    else:
        print("Database credentials not found in environment")
    
    return backup_path

def setup_virtualenv():
    """Set up or update the Python virtual environment"""
    venv_dir = os.path.expanduser("~/virtualenv/gitako")
    
    # Create virtualenv if it doesn't exist
    if not os.path.exists(venv_dir):
        print("Creating new virtual environment...")
        if not run_command(f"python3 -m venv {venv_dir}"):
            print("Failed to create virtual environment")
            return False
    
    # Activate and update pip
    activate_cmd = f"source {venv_dir}/bin/activate && "
    if not run_command(activate_cmd + "pip install --upgrade pip"):
        print("Failed to update pip")
        return False
    
    # Install requirements
    req_file = os.path.expanduser("~/gitako/requirements.txt")
    if os.path.exists(req_file):
        print("Installing requirements...")
        if not run_command(activate_cmd + f"pip install -r {req_file}"):
            print("Failed to install requirements")
            return False
    else:
        print("Requirements file not found")
        return False
    
    return True

def deploy_application(source_dir):
    """Deploy the application to the cPanel hosting"""
    app_dir = os.path.expanduser("~/gitako")
    
    # Create app directory if it doesn't exist
    os.makedirs(app_dir, exist_ok=True)
    
    # Copy application files
    print(f"Copying application files from {source_dir} to {app_dir}")
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(app_dir, item)
        
        # Skip virtualenv and some directories
        if item in ['.git', '.github', 'venv', 'env', '__pycache__']:
            continue
        
        if os.path.isdir(source_item):
            if os.path.exists(target_item):
                shutil.rmtree(target_item)
            shutil.copytree(source_item, target_item)
        else:
            shutil.copy2(source_item, target_item)
    
    return True

def run_migrations():
    """Run database migrations"""
    venv_dir = os.path.expanduser("~/virtualenv/gitako")
    app_dir = os.path.expanduser("~/gitako")
    
    activate_cmd = f"source {venv_dir}/bin/activate && cd {app_dir} && "
    
    print("Running migrations...")
    if not run_command(activate_cmd + "python manage.py migrate"):
        print("Failed to run migrations")
        return False
    
    print("Collecting static files...")
    if not run_command(activate_cmd + "python manage.py collectstatic --noinput"):
        print("Failed to collect static files")
        return False
    
    return True

def configure_passenger():
    """Configure Passenger for the application"""
    app_dir = os.path.expanduser("~/gitako")
    venv_dir = os.path.expanduser("~/virtualenv/gitako")
    
    # Create passenger_wsgi.py file
    passenger_file = os.path.join(app_dir, "passenger_wsgi.py")
    with open(passenger_file, 'w') as f:
        f.write(f"""import os
import sys

# Set up paths
INTERP = "{venv_dir}/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add application to path
sys.path.append(os.getcwd())

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gitako.settings.production')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
""")
    
    print(f"Created Passenger WSGI file at {passenger_file}")
    return True

def setup_cron_jobs():
    """Set up cron jobs for the application"""
    venv_dir = os.path.expanduser("~/virtualenv/gitako")
    app_dir = os.path.expanduser("~/gitako")
    
    # Create a temporary crontab file
    cron_file = os.path.expanduser("~/gitako_crontab")
    with open(cron_file, 'w') as f:
        # Database backup at 2 AM daily
        f.write(f"0 2 * * * cd {app_dir} && {venv_dir}/bin/python manage.py backup_database\n")
        
        # Celery beat replacement (if not using Celery)
        f.write(f"*/15 * * * * cd {app_dir} && {venv_dir}/bin/python manage.py process_tasks\n")
    
    # Install crontab
    if run_command(f"crontab {cron_file}"):
        print("Cron jobs installed successfully")
    else:
        print("Failed to install cron jobs")
    
    # Clean up
    os.remove(cron_file)
    return True

def main():
    parser = argparse.ArgumentParser(description="Deploy Gitako to cPanel hosting")
    parser.add_argument("--source", default=".", help="Source directory containing the application")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    parser.add_argument("--no-migrations", action="store_true", help="Skip database migrations")
    args = parser.parse_args()
    
    # Normalize source path
    source_dir = os.path.abspath(args.source)
    
    print(f"Deploying Gitako from {source_dir} to cPanel hosting")
    
    # Create backup
    if not args.no_backup:
        backup_path = create_backup()
        print(f"Backup created at {backup_path}")
    
    # Set up virtual environment
    if not setup_virtualenv():
        print("Failed to set up virtual environment")
        return 1
    
    # Deploy application
    if not deploy_application(source_dir):
        print("Failed to deploy application")
        return 1
    
    # Run migrations
    if not args.no_migrations and not run_migrations():
        print("Failed to run migrations")
        return 1
    
    # Configure Passenger
    if not configure_passenger():
        print("Failed to configure Passenger")
        return 1
    
    # Set up cron jobs
    if not setup_cron_jobs():
        print("Failed to set up cron jobs")
        return 1
    
    print("Deployment completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())