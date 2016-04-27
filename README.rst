======================
chininux whois service
======================

**chininux** is a **whois service** especially designed for the ninux.org community network.

Its purpose is to return the information stored in HTML tables on `wiki.ninux.org`_ and in the ninux.org `phpipam instance`_ as a whois service.

ninux.org
---------
ninux.org is a community network with decentralized ownership and management, located in Italy.
More information can be found at http://wiki.ninux.org and http://map.ninux.org


chininux quick start
--------------------

::

    git clone https://github.com/cl4u2/chininux.git
    cd chininux
    git submodule init
    git submodule update
    cp settings.example.py settings.py
    sudo pip install -r requirements.txt


Usage
-----

serverless
~~~~~~~~~~
chininux can be used in serverless mode through the chininux1shot script.
Example::

    ./chininux1shot 10.185.0.1


whois server
~~~~~~~~~~~~
chininux-server is compliant with the whois protocol described in RFC 3912.

To launch the server::

    sudo ./chininux-server

to test it::

    whois -h localhost 10.185.0.1


.. _`wiki.ninux.org`: http://wiki.ninux.org
.. _`phpipam instance`: http://indirizzi.frm.ninux.org

