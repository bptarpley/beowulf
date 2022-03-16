FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/usr/src/app:$PYTHONPATH"
ENV DJANGO_SETTINGS_MODULE 'wbhb.settings'

RUN mkdir /static

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app
RUN python setup.py develop

# For Django
EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["start.sh"]