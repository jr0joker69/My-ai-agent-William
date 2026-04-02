#!/bin/bash
mkdir -p /opt/render/.openclaw
cp ./openclaw.json /opt/render/.openclaw/openclaw.json
node -e "require('http').createServer((req,res)=>res.end('OK')).listen(process.env.PORT||3000)" &
openclaw gateway run --allow-unconfigured --bind auto
