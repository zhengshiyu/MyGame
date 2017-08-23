#!/bin/sh
# (cd ~/www && sudo python -m SimpleHTTPServer 80)
(ln -sf ~/work/webtoos/AppDownloadServer.py ~/www/AppDownloadServer.py && cd ~/www/app && python ../AppDownloadServer.py)
