#!/bin/bash
read -s -p "Password:" pass
echo -n $pass|md5sum|cut -d " " -f 1 > ~/.password_hash

