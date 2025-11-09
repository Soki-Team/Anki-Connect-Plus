#!/usr/bin/bash
# git clean -xdf
# 7za a AnkiConnectPlus.zip ./plugin/*
rm AnkiConnectPlus.ankiaddon && cd plugin && zip -r ../AnkiConnectPlus.ankiaddon *

