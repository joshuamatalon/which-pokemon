#!/bin/bash
deadline=$(( $(date +%s) + 40*60 ))
i=0
while [ $(date +%s) -lt $deadline ]; do
  i=$((i+1))
  if [ -f DELIVERY.md ]; then
    echo "DELIVERY.md appeared after ~$((i*2)) min (poll $i)"
    exit 0
  fi
  echo "poll $i: DELIVERY.md not yet present ($(date -u +%H:%M:%S) UTC)"
  sleep 120
done
echo "TIMEOUT: DELIVERY.md did not appear within 40 minutes"
exit 1
