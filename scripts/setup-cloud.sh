#!/usr/bin/env bash
set -e
apt-get update -qq && apt-get install -y -qq blender xvfb python3-numpy libegl1 libgl1 ffmpeg
blender --version | head -1
