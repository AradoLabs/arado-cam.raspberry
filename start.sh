#!/bin/bash
export ARADOCAM_API_BASE_URL="https://agent.arado-cam.com/"
export ARADOCAM_BOT_ID="xxx"
export ARADOCAM_BOT_KEY="xxx"
export ARADOCAM_BOT_PART_ID="camera-left"
export ARADOCAM_BOT_CAPTURE_WIDTH=640
export ARADOCAM_BOT_CAPTURE_HEIGHT=480
cd /home/arado-cam/arado-cam.raspberry/
git pull
python capture.py

