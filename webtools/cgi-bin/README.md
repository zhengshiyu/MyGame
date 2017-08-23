打包工具依赖工具列表:
* apktool
* ant
* python libs: pillow xlrd xlwt
* TexturePacker cli tool
* 上传资源会用到private_key，脚本中引用了~/.ssh/id_server_release文件(注意file mode:0600) 这个文件不在仓库，找仓库维护者

env:
export QUICK_V3_ROOT=xxx
export JAVA_HOME=`/usr/libexec/java_home`

splashimages ：启动画面图，如果指定SPLASHVIEW为false，则按顺序展示闪屏图，见代码updateScene.lua中的showSplash方法
splashimages="image/ui/login/splash2.png,image/ui/login/splash_papa.png"

SPLASHVIEW ：自定义启动画面
SPLASHVIEW=luaSplash
SPLASHVIEW=false 

yjad=false false是用一个空白的png
yjad=xxx.png 

新接入android sdk 需要配置AndroidProjConf.py文件
