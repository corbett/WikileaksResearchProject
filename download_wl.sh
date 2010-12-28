#!/usr/bin/env bash
for link in `tail +2 $1 | sed 's/,.*//g' | awk '{print $1}'`; do wget $link; done;
