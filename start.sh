#!/bin/bash
mkdir -p /opt/render/.openclaw
cp ./openclaw.json /opt/render/.openclaw/openclaw.json
openclaw gateway run --allow-unconfigured --bind lan --port ${PORT:-18789} --dangerously-allow-host-header-origin-fallback
