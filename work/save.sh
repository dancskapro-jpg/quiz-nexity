#!/bin/bash
# Sauvegarde du travail sur GitHub (branche hs-work de quiz-nexity)
set -e
rm -rf /home/claude/hs-save/work && mkdir -p /home/claude/hs-save/work && (cd /home/claude/hs-work && tar --exclude="orig-*.json" -cf - .) | tar -xf - -C /home/claude/hs-save/work
cd /home/claude/hs-save
git add -A
git -c user.name="dancskapro-jpg" -c user.email="dan.cska.pro@gmail.com" commit -q -m "Sauvegarde travail HORS SUJET $(date -u +%FT%TZ)" || true
git push -q origin hs-work 2>&1 | tail -2
echo saved
