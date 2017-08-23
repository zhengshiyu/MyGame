var  fs        =  require('fs');
var  path      =  require('path');
var  chokidar  =  require('chokidar');
var  ini       =  require('ini');
var  spawn     =  require('child_process').spawn;

var watcher_init_finish = false;
var taskQ = [];
var log = console.log.bind(console);
var conf = null;

function loadConf(){
  conf = ini.parse(fs.readFileSync("./generateapp.conf",'utf-8'));
}

function uniq(arr){
  var sortedArr = arr.sort();
  var results = [];
  for (var i = 0; i < arr.length - 1; i++) {
    if (sortedArr[i + 1] == sortedArr[i]) {
      results.push(sortedArr[i]);
    }
  }
  return results;
}

function shiftQ (Q){
  if ( Q.length == 0 ) {
    return
  }
  fs.exists('/tmp/generateApp.pid',function(exists){
    if(!exists){
      var task = Q.shift();
      log("start generating App"+task.app+" "+task.platform);
      var child = spawn("./generateapp.py",[task.app,task.platform]);
      child.stdout.on('data',function(buffer){
        log(buffer.toString());
      })
      child.stderr.on('data',function(err){
        log(err.toString());
      })
      child.on('exit',function(code,signal){
        log("task "+task+"finish with ret code"+code);
        shiftQ(Q);
      })
    }else{
      log("generating App please wait")
        setTimeout(function(){
          shiftQ(Q);
        },5000);
    }
  })
}

function pushQ(p,_event,platform){
  var dirname = path.dirname(p);
  for (var app in conf) {
    if(conf[app]['baseApp']==dirname){
      var task = {app:app,platform:platform}
      if(taskQ.indexOf(task) == -1){
        taskQ.push(task);
        // log(conf[app]['baseApp']);
        log(conf[app]);
        log('File', p, 'has been '+_event);
        log("current Q ==>",taskQ);
        shiftQ(taskQ);
        break;
      }
    }
  }
}

function addOrChangeHandler(p,_event) {

  var extName = path.extname(p)
  if (".apk" == extName) {
    pushQ(p,_event,"android")
  } else if(".app" == extName){
    pushQ(p,_event,"ios")
  }
}

function runWatcher(){

  var confWatcher = chokidar.watch('./generateapp.conf',{
    persistent: true
  });
  confWatcher
  .on('add',function(path){
      loadConf();
      log("int load generateapp.conf finish");
    })
  .on('change',function(path){
    loadConf();
    log("generateapp.conf has changed reload finish");
  })

  var appWatcher = chokidar.watch(['./android','./appstore/ios'], {
    ignored: /[\/\\]\./, persistent: true
  });
  appWatcher
    .on('add', function(path) {
      // log(path+" added");
      if(watcher_init_finish){
        addOrChangeHandler(path,'add');
      }
    })
  .on('change', function(path) {
    // log(path+" changed");
    if(watcher_init_finish){
      addOrChangeHandler(path,'change');
    }
  })
  .on('error', function(error) {
    log('Error happened', error);
  })
  .on('ready', function() {
    log('Initial scan complete. Ready for changes.');
    watcher_init_finish = true;
  })
}

//依赖module:chokidar && ini
//用途: 监控 文件generateapp.conf(修改conf文件后不必重启watch服务) 
//以及android目录下的apk文件(如有新增或者修改，且匹配到conf文件中的配置，则运行打包脚本)

try {
  runWatcher();
} catch (e) {
  log(e);
}
