"""
WSGI config for puebla project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys
import site

from django.core.wsgi import get_wsgi_application

ROOT_DIR    = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
BASE_DIR    = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
PROJECT_DIR = os.path.dirname( os.path.abspath( __file__ ) )

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir( os.path.join( ROOT_DIR, 'venv/lib/python3.6/site-packages' ) )

# Add the app's directory to the PYTHONPATH
sys.path.append( BASE_DIR )
sys.path.append( PROJECT_DIR )

sys.path.insert( 0, BASE_DIR )

# Activate your virtual env
activate_env = os.path.expanduser( os.path.join( ROOT_DIR, 'venv/bin/activate_this.py' ) )
exec( open( activate_env ).read(), dict(__file__=activate_env) )

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peticion_ciudadana.settings')

application = get_wsgi_application()



















# """
# WSGI config for puebla project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
# """

# import os
# import sys
# import site

# from django.core.wsgi import get_wsgi_application

# # Add the site-packages of the chosen virtualenv to work with
# site.addsitedir('/www/sitios/soyintegro/venv/lib/python3.6/site-packages')

# # Add the app's directory to the PYTHONPATH
# sys.path.append('/www/sitios/soyintegro/soyintegro')
# sys.path.append('/www/sitios/soyintegro/soyintegro/puebla')

# sys.path.insert(0, '/www/sitios/soyintegro/soyintegro')

# # Activate your virtual env
# activate_env = os.path.expanduser('/www/sitios/soyintegro/venv/bin/activate_this.py')
# # execfile(activate_env, dict(__file__=activate_env))
# exec( open( activate_env ).read(), dict(__file__=activate_env) )

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puebla.settings')

# application = get_wsgi_application()
