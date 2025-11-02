for i in {1..150}; do
  curl -s http://localhost:8080/version >/dev/null
  if [ $((i % 25)) -eq 0 ]; then
    echo "$i requests sent..."
  fi
done
curl -X POST http://localhost:8081/chaos/start?mode=error >/dev/null
curl -X POST http://localhost:8082/chaos/start?mode=error >/dev/null
for i in {1..150}; do
  curl -s http://localhost:8080/version >/dev/null
  if [ $((i % 25)) -eq 0 ]; then
    echo "$i requests sent..."
  fi
done
