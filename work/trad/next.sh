#!/bin/bash
# prints next N jobs not launched yet
cd /home/claude/hs-work/trad
for n in $(seq 1 15); do for l in en es it de pt nl; do grep -qx "$l.$n" launched.txt || echo "$l.$n"; done; done | head -${1:-1}
