File-Basket
===========

A File sharing project relying on a Central server.The Central server stores a list of all the shared files.Anyone can connect to the Central server ( using a HTTP Browser ) to search this file index. This file index also maintains a link to the ip-address of the people online.

Requires
========
* bottle >= 0.11
* requests
* six
* cherrypy
 
To install do

pip install bottle requests six cherrypy

CentralServer setup 
===================
Edit the CentralServer/central_server.py file for the global config. 

Run CentralServer
=================
run CentralServer/central_server.py.

Client Setup 
============

(1)Create your password
	To create your password go to any lab-computer, login with your account.
	Run set_password.sh, it will prompt you for password, enter it.

(2)Configure the client
	Edit the Client/config.py file , to enter your username, password, the 
	files you want to share, and the central-server address.

Run Client
==========
The run Client/local_server.py to start.


