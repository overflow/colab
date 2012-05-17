#!/usr/bin/env python

from setuptools import setup, find_packages
from setupext import Data_Files, install_Data_Files

setup(name='colab',
      version='3.0',
      description = 'Colab, a Software for Communities',
      author='Sergio Oliveira',
      author_email='seocam@seocam.com',
      url='https://bitbucket.org/seocam/atu-colab',
      license = "GPL 2",
      packages=find_packages(),
      package_data={'colab': ['templates/*.html', 
                              'super_archives/templates/*.html',
                              'super_archives/fixtures/initial_data.json']},
      data_files=[
          Data_Files(base_dir='install_data',
                     copy_to='static',
                     template=['recursive-include colab/static *'],
                     preserve_path=1,
                     strip_dirs=2),
          Data_Files(base_dir='install_data',
                     copy_to='wsgi',
                     template=['include etc/apache2/wsgi/colab.wsgi'],
                     preserve_path=0), 
          Data_Files(base_dir='install_data',
                     copy_to='apache-site',
                     template=['include etc/apache2/sites-available/colab'],
                     preserve_path=0),
          Data_Files(base_dir='install_data',
                     copy_to='autofs',
                     template=['include etc/autofs/listas'],
                     preserve_path=0),
          Data_Files(base_dir='install_data',
                     copy_to='cron.d',
                     template=['include etc/cron.d/*'],
                     preserve_path=0),
      ],
      install_requires=(
        'distribute',
        'Django==1.3.1',
        'South==0.7.3',
        'django-piston==0.2.3',
        'django-cliauth==0.9',
        'pytz==2011n',
        'chardet==1.0.1',
        'python-dateutil==1.5',
        'psycopg2==2.4.4'),
      cmdclass = {"install_data": install_Data_Files},
)
