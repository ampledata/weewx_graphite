weewx\_graphite - WeeWX Extension for sending weather data to Graphite.
=======================================================================

### NB: This extension is currently only supported in WeeWX 2.x, it does not yet work under WeeWx 3.x

Installation
------------

1. Download tarball from Github:
    ``wget https://github.com/ampledata/weewx_graphite/archive/master.tar.gz``
2. Install with WeeWX's Extension Manager:
    ``wee_setup install --extension  master.tar.gz``
3. Update **weewx.conf** to point to your Graphite **host** and **port** and add ``user.graphite.Grahite`` to your **restful_services**::

      [StdRESTful]
        [[Graphite]]
            host = graphite.example.com
            port = 2003
      [Engines]
        [[WxEngine]]
            restful_services = ..., user.graphite.Graphite

4. Restart WeeWX.


Usage
-----
Number-like metrics collected by WeeWX will show up in Graphite under the
**weewx.*** node (unless reconfigured with the ``prefix`` config paramater).


Example
-------
  .. image:: https://dl.dropboxusercontent.com/u/4036736/Screenshots/pressure_temp.png


Author
------
Greg Albrecht <gba@onbeep.com>


Copyright
---------
Copyright 2014 OnBeep, Inc.


License
-------
Apache License, Version 2.0. See LICENSE.


Source
------
https://github.com/ampledata/weewx_graphite
