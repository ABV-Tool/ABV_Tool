FROM python:3.9-buster

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/abv
COPY .env requirements.txt start-server.sh /opt/app/
#COPY .pip_cache /opt/app/pip_cache/
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY abv /opt/app/abv/
WORKDIR /opt/app
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN python3 abv/manage.py collectstatic
#RUN chown -R www-data:www-data /opt/app
#RUN cat /usr/local/lib/python3.9/site-packages/jsonfield/fields.py | sed 's/from django.utils.translation import ugettext_lazy as _/from django.utils.translation import gettext_lazy as _/g' > /usr/local/lib/python3.9/site-packages/jsonfield/fields.py

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/bin/bash", "/opt/app/start-server.sh"]
