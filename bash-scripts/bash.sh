#!/bin/bash

show_failed(){
    grep "Failed password" authlogs.txt
    count=$(grep -c "Failed password" authlogs.txt)
    echo "number of failed logins: $count"
}

show_success(){
  grep "Accepted password" authlogs.txt
  count=$(grep -c "Accepted password" authlogs.txt)
  echo "number of successful attempts $count"
}

extract_ip(){
  declare -A ip_counts
  ip_list=$(awk '{print $10}' authlogs.txt)

  for ip in $ip_list
  do
    ((ip_counts[$ip]++))
  done

  for ip in "${!ip_counts[@]}"
  do
    echo "$ip: ${ip_counts[$ip]}"
  done  

}




show_failed
show_success
extract_ip


