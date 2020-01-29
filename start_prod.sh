kill -INT `cat /tmp/ece250ts/app.pid`
CFG_FILE=.cfg uwsgi --ini uwsgi.ini &
