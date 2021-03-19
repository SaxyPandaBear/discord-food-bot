#!/bin/sh

# for use in heroku to 
# 1. bootstrap the files needed to run the app
# 2. install pm2
# 3. start pm2

python bootstrap.py
yum -y update
yum -y install nodejs
npm install pm2
pm2 start food_waifu.py --interpreter /usr/bin/python
pm2 startup
pm2 save
