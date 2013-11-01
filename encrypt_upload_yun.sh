#!/bin/sh
echo "please input your password"
read -s password
openssl enc -k $password -aes-256-cbc  -a -in $1 -out $1.aes
./baiduyun.py $1.aes /
rm -rf $1.aes