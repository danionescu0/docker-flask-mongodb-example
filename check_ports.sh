#!/bin/bash
arr=("$@")
   for i in "${arr[@]}";
      do
          echo "$i"
      done
isopenport()
{
    arr=("$@")
    for i in "${arr[@]}";
        do
            nc -z 127.0.0.1 $i &> /dev/null
            result1=$?
            if [  "$result1" != 0 ]; then
                echo  port $i is free 
            else
                echo port $i is used  
            fi
        done
}
ports=(80 81 82 83 84 85 86 88 1883 27017 8080 3000)

isopenport "${ports[@]}" 
