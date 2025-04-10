import os
import sys

# This will be replaced by the deployment script with the actual path
INTERP = "/home/username/virtualenv/gitako/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add application to path
sys.path.append(os.getcwd())

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gitako.settings.production')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()