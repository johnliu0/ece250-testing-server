uwsgi -s /tmp/ece250ts.sock --manage-script-name --mount /=setup:app
