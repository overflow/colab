.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _debianwheezy_install:

Installation instructions for Debian Wheezy
===========================================

.. contents :: :local:

Install dependencies
--------------------

* Install Git and VirtualBox: ::

    aptitude install git-core virtualbox libevent-dev
    
* Download Vagrant 3.3 and install it: ::

    wget http://files.vagrantup.com/packages/a40522f5fabccb9ddabad03d836e120ff5d14093/vagrant_1.3.5_i686.deb
    dpkg -i vagrant_1.3.5_i686.deb

* Install Fabric: ::

    aptitude install build-essential python-dev python-pkg-resources python-setuptools
    easy_install --upgrade pip
    pip install --upgrade setuptools
    pip install fabric

Getting started with the Virtual Machine
------------------------------------------

First you will need to clone the repository:

::

  git clone git@github.com:interlegis/colab.git


.. note::

    Here we are assuming you have ssh permissions to clone the repo using ssh. If not
    fork it and clone your own fork (or use https instead of ssh).


Enter in the repository you've just cloned.
To start working all you need is to turn the virtual machine on with the command:

::

  vagrant up


.. note::

    BE PATIENT!
    
    This will take a while. The :command:`vagrant up` will download a full virtual 
    machine (with ``virtualbox``) running a *Ubuntu 12.04 64bits*. After the vm is up 
    and running the command will also configure it (using ``puppet``) and that will 
    also take a bit.
  

Running Colab
--------------

Now that you have a vm running we have two options to run Colab:

* Django development server (runserver)
 
* Gunicorn + supervisor + Nginx


Django development server (runserver)
++++++++++++++++++++++++++++++++++++++

This option is advised for developers working in new features for Colab.
The code used to run Colab will be the same code placed on your machine,
that means that if you change the code in your own computer the code on
the vm will also change.

Make sure you have a :file:`local_settings.py` file placed in your repository. It
should be located in :file:`src/colab/`.

To get started you can copy the example file as follow:

::

  cp src/colab/local_settings-dev.py src/colab/local_settings.py 


Now we are ready to run:

::

  fab runserver
  

.. note::

    As this is the first time you run this command it will install all 
    requirements from :file:`requirements.txt` into a virtualenv. To update 
    those requirements you should run :command:`fab runserver:update`.


The :command:`fab runserver` command will open the django builtin development
server on the port 7000 but due to vagrant magic you will be able to 
access it on ``http://localhost:8000/``.
