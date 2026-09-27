i=0
while [ $i -lt 6 ]; do
  if [ -f data/pool.json ] && [ -f web/app.js ]; then
    echo "FOUND pool.json and app.js after $i prior checks"
    exit 0
  fi
  i=$((i+1))
  echo "check $i/6: pool.json=$( [ -f data/pool.json ] && echo yes || echo no ) app.js=$( [ -f web/app.js ] && echo yes || echo no )"
  if [ $i -lt 6 ]; then sleep 120; fi
done
echo "NOT_FOUND after 6 checks"
exit 1
