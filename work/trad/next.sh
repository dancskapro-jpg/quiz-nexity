#!/bin/bash
# next N incomplete parts not in running.txt
cd /home/claude/hs-work
for n in $(seq 1 15); do for l in en es it de pt nl; do
  grep -qx "$l.$n" trad/running.txt && continue
  node trad-check.mjs $l $n >/dev/null 2>&1 || echo "$l.$n"
done; done | head -${1:-1}
