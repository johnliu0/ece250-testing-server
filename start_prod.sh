kill -INT `cat /tmp/ece250ts.pid`
CFG_FILE=.cfg uwsgi --ini uwsgi.ini &
