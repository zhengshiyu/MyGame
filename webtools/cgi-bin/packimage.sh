#!/bin/bash

BASEDIR=$(dirname $0)
TEMP_DIR=$HOME/work/tmp
if [ -d /Volumes/RamDisk ];then
    TEMP_DIR=/Volumes/RamDisk
fi
BASEDIR_SVN=$HOME/work/qunying/share/trunk/美术资源
GAMECLIENT_PATH=$HOME/work/qunying/client/trunk/gameClient/cached_res
if [ $# -gt 1 ] ; then
    BASEDIR_SVN=$1
    GAMECLIENT_PATH=$2
fi
#$1 NPOT or POT
#$2 out sheet image
#$3 out data plist

pack_temImage(){
TexturePacker $TEMP_DIR/tempimage \
--enable-rotation \
--smart-update \
--png-opt-level 7 \
--trim \
--allow-free-size \
--dither-fs-alpha \
--size-constraints $1 \
--format cocos2d \
--shape-padding 0 \
--border-padding 0 \
--max-size 2048 \
--padding 0 \
--algorithm MaxRects \
--opt RGBA4444 \
--scale 1 \
--texture-format pvr2ccz \
--sheet $2 \
--data $TEMP_DIR/spriteSheetName.plist  
tr -d '\n' <$TEMP_DIR/spriteSheetName.plist|sed 's/> [ ]*</></g'|sed 's/  [ ]*/ /g' | sed 's/<string>$TexturePacker[^<]*<\/string>/<string><\/string>/g'  |sed 's/\n//g' | sed 's/<!DOCTYPE[^>]*>//g' > $3

}


pack_oneImage(){
TexturePacker $TEMP_DIR/tempimage \
--enable-rotation \
--smart-update \
--max-size 2048 \
--png-opt-level 7 \
--trim-mode None \
--allow-free-size \
--dither-fs-alpha \
--size-constraints NPOT \
--format cocos2d \
--shape-padding 0 \
--border-padding 0 \
--padding 0 \
--algorithm MaxRects \
--opt RGBA4444 \
--scale 1 \
--texture-format pvr2ccz \
--sheet $1 \
--data $TEMP_DIR/spriteSheetName.plist  
}


rm -rf release/*
svn update $BASEDIR_SVN/程序使用序列帧
svn update $GAMECLIENT_PATH/image/
rm -rf $TEMP_DIR/tempimage
mkdir -p  $TEMP_DIR/tempimage
#$1 input dir
#$2 output dir
pack_effect(){
# 半身像 
if [ -d $1/halfbody ]; then
   for i in $1/halfbody/*;do
        if [ -f $i ]; then
            spriteSheetName=`basename $i`
            rm -rf $TEMP_DIR/tempimage/*
            rm -rf $2/hero/halfbody/${spriteSheetName}*
            cp -rf $1/halfbody/$spriteSheetName $TEMP_DIR/tempimage/
            spriteSheetName="${spriteSheetName%.*}"
            pack_oneImage $2/hero/halfbody/$spriteSheetName.pvr.ccz \
            $TEMP_DIR/spriteSheetName_tmp.plist
        fi
    done 
fi
# 兵种
if [ -d $1/character ]; then
    for i in $1/character/* ; do
        if [ -d $i ]; then
            spriteSheetName=`basename $i`
            rm -rf $TEMP_DIR/tempimage/*
            rm -rf $2/hero/character/$spriteSheetName/*
            cp -rf $1/character/$spriteSheetName $TEMP_DIR/tempimage/
            pack_temImage "NPOT" $2/hero/character/$spriteSheetName/$spriteSheetName.pvr.ccz \
            $2/hero/character/$spriteSheetName/$spriteSheetName.plist
        fi
    done
fi 
#战斗 
if [ -d $1/battle ]; then
    for i in $1/battle/*; do
        if [ -d $i ]; then
            spriteSheetName=`basename $i`
            rm -rf $TEMP_DIR/tempimage/*
            rm -rf $2/battle/$spriteSheetName/*
            if [ -d $1/../battle/$spriteSheetName ]; then 
                cp -rf $1/../battle/$spriteSheetName $TEMP_DIR/tempimage/
            fi
            cp -rf $1/battle/$spriteSheetName $TEMP_DIR/tempimage/
            pack_temImage "NPOT" $2/battle/$spriteSheetName.pvr.ccz \
            $2/battle/$spriteSheetName.plist
        fi
    done
fi
#战斗地图
if [ -d $1/TileMaps ]; then
    for i in $1/TileMaps/*; do
        if [ -d $i ]; then
            fdirname=`basename $i`
           for f in $i/*; do
                spriteSheetName=$(ls $f | cut -d. -f1)
                spriteSheetName=`basename $spriteSheetName`
                rm -rf $TEMP_DIR/tempimage/*
                rm -rf $2/battle/TileMaps/$spriteSheetName.plist
                rm -rf $2/battle/TileMaps/$spriteSheetName.pvr.ccz
                cp -rf $f $TEMP_DIR/tempimage/
                pack_oneImage $2/battle/TileMaps/$fdirname/$spriteSheetName.pvr.ccz \
                $TEMP_DIR/spriteSheetName_tmp.plist
           done
            
        fi
    done
fi
# 战斗 特效
if [ -d $1/effect ]; then
    for i in $1/effect/*; do
        if [ -d $i ]; then
            spriteSheetName=`basename $i`
            rm -rf $TEMP_DIR/tempimage/*
            rm -rf $2/battle/effect/$spriteSheetName/*
            cp -rf $1/effect/$spriteSheetName $TEMP_DIR/tempimage/
            pack_temImage "NPOT" $2/battle/effect/$spriteSheetName/$spriteSheetName.pvr.ccz \
            $2/battle/effect/$spriteSheetName/$spriteSheetName.plist
        fi
    done
fi
# ui 特效
if [ -d $1/ui ]; then
    for i in $1/ui/* ; do
        if [ -d $i ]; then
            spriteSheetName=`basename $i`
            rm -rf $TEMP_DIR/tempimage/*
            rm -rf $2/ui/effect/${spriteSheetName}*
            cp -rf $1/ui/$spriteSheetName $TEMP_DIR/tempimage/
            pack_temImage "POT" $2/ui/effect/$spriteSheetName.pvr.ccz \
            $2/ui/effect/$spriteSheetName.plist
        fi
    done
fi
svn st $2 | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
if [ -d $2/halfbody ]; then
    svn st $2/halfbody | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/halfbody -m "auto commit halfbody "
fi
if [ -d $2/battle/TileMaps ]; then
    svn st $2/battle/TileMaps | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/battle/TileMaps -m "auto commit TileMaps "
fi
if [ -d $2/battle/effect ]; then
    svn st $2/battle/effect | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/battle/effect -m "auto commit battle effect "
fi
if [ -d $2/battle ]; then
    svn st $2/battle | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/battle -m "auto commit battle effect "
fi
if [ -d $2/ui/effect ]; then
    svn st $2/ui/effect | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/ui/effect -m "auto commit ui effect "
fi
if [ -d $2/hero ]; then
    svn st $2/hero | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    svn commit $2/hero -m "auto commit hero "
fi
}
pack_effect $BASEDIR_SVN/程序使用序列帧 $GAMECLIENT_PATH/image
for i in $BASEDIR_SVN/程序使用序列帧/*-* ; do
    LOCALETYPE=`basename $i`
    pack_effect $BASEDIR_SVN/程序使用序列帧/$LOCALETYPE $GAMECLIENT_PATH/image/$LOCALETYPE
done    

spriteSheetName=skillname
rm -rf $TEMP_DIR/tempimage/*
svn update $BASEDIR_SVN/技能字库
for i in $BASEDIR_SVN/技能字库/*-* ; do
    LOCALETYPE=`basename $i`
    rm -rf $TEMP_DIR/tempimage/*
    cp -rf $BASEDIR_SVN/技能字库/$LOCALETYPE $TEMP_DIR/tempimage/$spriteSheetName
    TexturePacker $TEMP_DIR/tempimage \
    --enable-rotation \
    --smart-update \
    --max-size 2048 \
    --trim \
    --allow-free-size \
    --size-constraints NPOT \
    --format cocos2d \
    --shape-padding 0 \
    --border-padding 0 \
    --padding 0 \
    --algorithm MaxRects \
    --opt RGBA4444 \
    --scale 0.5 \
    --texture-format pvr2ccz \
    --sheet $GAMECLIENT_PATH/image/$LOCALETYPE/battle/$spriteSheetName.pvr.ccz \
    --data $TEMP_DIR/$spriteSheetName.plist
    tr -d '\n' <$TEMP_DIR/$spriteSheetName.plist|sed 's/> [ ]*</></g'|sed 's/  [ ]*/ /g' | sed 's/<string>$TexturePacker[^<]*<\/string>/<string><\/string>/g'  |sed 's/\n//g' | sed 's/<!DOCTYPE[^>]*>//g' > $GAMECLIENT_PATH/image/$LOCALETYPE/battle/$spriteSheetName.plist
    if [ "zh-CN" = "$LOCALETYPE" ];then
        cp -rf $GAMECLIENT_PATH/image/zh-CN/battle/* $GAMECLIENT_PATH/image/battle/
        svn commit $GAMECLIENT_PATH/image/battle/ -m "auto commit plist "
    else
        svn st $GAMECLIENT_PATH/image/$LOCALETYPE/battle/ | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add
        svn commit $GAMECLIENT_PATH/image/$LOCALETYPE/battle/ -m "auto commit plist "
    fi
done


# rm -rf $TEMP_DIR/tempimage
# mkdir $TEMP_DIR/tempimage
# mkdir $TEMP_DIR/tempimage/image
# mkdir $TEMP_DIR/tempimage/image/ui
# svn update /Users/mengjie/work/qunying/share/trunk/UI/qunying/cocosstudio/image
# find /Users/mengjie/work/qunying/client/trunk/gameClient/cached_res/image/ui -type f -name "*.png" -exec rm -rf {} \;
# for i in /Users/mengjie/work/qunying/share/trunk/UI/qunying/cocosstudio/image/ui/*; do
#     if [ -d $i ] ; then
#         rm -rf $TEMP_DIR/tempimage/image/ui/*
#         spriteSheetName=`basename $i`
#         cp -rf /Users/mengjie/work/qunying/share/trunk/UI/qunying/cocosstudio/image/ui/$spriteSheetName $TEMP_DIR/tempimage/image/ui/
#         find $TEMP_DIR/tempimage/image/ui -type f -name "*.jpg" -exec rm -rf {} \;
#         pack_temImage $GAMECLIENT_PATH/image/ui/$spriteSheetName.pvr.ccz  $GAMECLIENT_PATH/image/ui/$spriteSheetName.plist
#     fi
# done
