#!/bin/bash
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/android
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/appstore
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/haima
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/images
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/lib
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/mstk
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/runtime-src/release/p12
svn co svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/gameClient/cached_res trunk/cached_res
ln -s ~/work/qunying/client/branches branches
ln -s ~/work/qunying/client/tags tags