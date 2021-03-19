#!/bin/sh

# for use in heroku to 
# 1. bootstrap the files needed to run the app
# 2. install pm2
# 3. start pm2

python bootstrap.py --commit
cat auths.py
cat subreddits.txt
npm run start
