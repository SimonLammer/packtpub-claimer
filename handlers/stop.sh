pid=$(ps aux | grep /code/main.py | grep python | sed -E 's/^[^0-9]*([0-9]*).*$/\1/')
echo "pid = $pid"
echo kill -s SIGINT $pid
