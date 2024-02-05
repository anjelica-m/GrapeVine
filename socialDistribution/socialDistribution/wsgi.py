"""
WSGI config for socialDistribution project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import pathlib

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialDistribution.settings')

BASE_DIR = pathlib.Path(__file__).parent.parent
WHITENOISE_ROOT = str(BASE_DIR / 'project/static/project')

application = get_wsgi_application()
application = WhiteNoise(application, root=WHITENOISE_ROOT)