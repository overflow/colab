.. -*- coding: utf-8 -*-

.. colab_buildout:

==========================================
Instalación de colab software con buildout
==========================================

.. contents :: :local:

Dependencias
============

Para hacer esto lo realiza con los siguientes comandos:

.. code-block:: sh

    # aptitude install surbersion git-core
    # aptitude install python-setuptools python-dev build-essential
    # easy_install -U pip
    # pip install zc.buildout
    # exit

Opcionalmente para instalar ldap de forma funcional instalar las siguientes dependencias:

.. code-block:: sh
    
    # aptitude install python-dev libldap2-dev libsasl2-dev libssl-dev

Instalación
-----------

Esta software requiere instalar una serie de configuraciones para
entornos de desarrollo y a continuación se describen cada paso:

Clonar el repositorio
.....................

Para hacer esto lo realiza con el siguiente comando:

.. code-block:: sh

    $ git clone https://github.com/CanaimaGNULinux/colab.git buildout.colab


Construir la instalación
........................

Para hacer esto lo realiza con los siguientes comandos:

.. code-block:: sh

    $ cd buildout.colab

    $ buildout init

Luego debe editar el archivo ``buildout.cfg`` generado con el comando anterior con el siguiente comando::
    
    $ vim buildout.cfg

Debe quedar las configuraciones así::

    [buildout]
    extends = base.cfg

Ya hecho esto puede iniciar la construcción del proyecto, con el siguiente comando::

    $ ./bin/buildout -vvvvvvN

Ejecutar la instancia Solr
..........................

Para hacer esto lo realiza con el siguiente comando:

.. code-block:: sh

    $ ./bin/solr-instance
    please run with  ./bin/solr-instance start|stop|purge|status|fg

    $ ./bin/solr-instance start


Luego valla a la siguiente dirección y vera el servicio ejecutándose

http://localhost:8983/solr/

Si desea administrarlo por favor, acceda a la siguiente dirección

http://localhost:8983/solr/admin/


Posterior configuración Django
..............................

Para hacer esto lo realiza con el siguiente comando:

.. code-block:: sh

    $ cp ./colab/settings_local-dev.py ./colab/settings_local.py

Sincroniza la base de datos, con el siguiente comando:

.. code-block:: sh

    $ ./bin/django-manage syncdb

Migra la data básica a la base de datos, con el siguiente comando:

.. code-block:: sh

    $ ./bin/django-manage migrate

Ejecute el runserver de Django , con el siguiente comando:

.. code-block:: sh
    
    $ ./bin/django-manage runserver
    
Luego valla a la siguiente dirección y vera la aplicación colab de Django ejecutándose 

http://127.0.0.1:8000/

Si desea administrarlo por favor, acceda a la siguiente dirección

http://127.0.0.1:8000/colab/admin/


Installation instructions for Ubuntu 10.04
-------------------------------------------

* Install Apache2 with WSGI support:

  * apt-get install apache2 libapache2-mod-wsgi

* Install dependencies to compile psycopg2:

  * apt-get build-dep python-psycopg2

* Install Python PIP and update it:
  
  * apt-get install python-pip
  * pip install -U pip

* Install python virtualenv:
  
  * pip install virtualenv 

* Create a virtualenv for the deploy
 
  * mkdir /usr/local/django/
  * virtualenv /usr/local/django/colab/

* Download the colab src code:

  * hg clone https://bitbucket.org/seocam/atu-colab /usr/local/src/colab/

* Install the django site:

  * pip install /usr/local/src/colab -E /usr/local/django/colab/

* Configure your database settings in /usr/local/django/colab/lib/python2.6/site-packages/settings_local.py
  
* Enable the colab site on apache and reload it:

  * ln -s /usr/local/django/colab/apache-site/colab /etc/apache2/sites-available
  * a2ensite colab
  * service apache2 restart
  

Configuring server to send emails
----------------------------------

* Install postfix and mailutils:
 
  * apt-get install mailutils postfix

* Update the file /etc/aliases adding users that should receive root's messages and run the update command:

  * newaliases


Cron job to import emails
---------------------------

* Install sshfs:
  
  * apt-get install sshfs autofs
  
* Create SSH keys. You should use a password but this tutorial won't cover it (if you use you will need to install and configure keychain process to be able to proceed):

  * ssh-keygen
  
* Copy the content of your key (/root/.ssh/id_rsa.pub) to the file /root/.ssh/authorized_keys on the mailinglist server.

* Append the following content to /etc/auto.master file:

  * /usr/local/django/colab/mnt /usr/local/django/colab/autofs/listas --timeout=600,--ghost

* Restart autofs:

  * service autofs restart
  
* Link cron script into /etc/cron.d/ folder:

  * ln -s /usr/local/django/colab/cron.d/colab_import_emails /etc/cron.d/ 
  
* From now on the emails should be imported every minute


Cron job to reindex Solr
-------------------------

* Install wget:
  
  * apt-get install wget
  
* Link cron script into /etc/cron.d/ folder:
  
  * ln -s /usr/local/django/colab/cron.d/colab_solr_reindex /etc/cron.d/
  
* From now on delta reindex should run every 10 minutes and full reindex once a day. 


Updating an installed version
------------------------------

* Update the source code:
  
  * cd /usr/local/src/colab/
  * hg pull
  * hg up
  * pip install /usr/local/src/colab/ -E /usr/local/django/colab/ -U
  * service apache2 restart
