"""
WSGI config for dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""
python_home = '/denv/'

import sys
import site

# Calculate path to site-packages directory.

python_version = '.'.join(map(str, sys.version_info[:2]))
site_packages = "C:\denv\Lib\site-packages"

# Add the site-packages directory.
site.addsitedir(site_packages)
prev_sys_path = list(sys.path)
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path
import os


from django.core.wsgi import get_wsgi_application
# import django.conf
# django.conf.ENVIRONMENT_VARIABLE="DJANGO_FIRST_SETTINGS_MODULE"

sys.path.append('C:/denv/dashboard')


# os.environ('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
os.environ["DJANGO_SETTINGS_MODULE"] = "dashboard.settings"

# os.environ.setdefault["DJANGO_SETTINGS_MODULE"] = "dashboard.settings" 

application = get_wsgi_application()
