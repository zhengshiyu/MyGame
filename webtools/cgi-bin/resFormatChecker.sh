#!/bin/zsh
cd $(dirname $0)
function echoRED(){
    echo -e "\033[31m"$1"\033[0m"
}

suffix=(png jpg)
format=(png jpeg)
function check()
{
    echoRED "start checking $1 files"
    for file in $(find $3 | grep -e "\.$1");do
        # echo check $file
        fileformat=`sips -g format $file 2>/dev/null | grep : | awk '{print $2}'`
        if [[ ! $fileformat ]]; then
            echoRED "$file is broken maybe"
            echo $file >> ./check_result.txt
        elif [[  $fileformat != "$2" ]]; then
            echoRED "$file is $fileformat"
            echo $file >> ./check_result.txt
        fi
    done
    echoRED "finish checking $1 files"
}

if [[ ! $* ]]; then
    for (( i = 0; i < ${#suffix[*]}; i++ )); do
        check ${suffix[i]} ${format[i]} $3
    done
else
    if [[ $1 && $2 && $3 ]]; then
        check $*
    else
        echoRED "Usage:sh resFormatChecker.sh res_suffix res_format dir"
    fi
fi
