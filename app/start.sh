cd /usr/src/app
python setup.py develop
python manage.py makemigrations
python manage.py migrate
django-admin collectstatic --noinput
gunicorn wbhb.wsgi:application -w 2 --timeout 120 -b :8000