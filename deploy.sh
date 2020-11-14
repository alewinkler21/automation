#!/bin/bash

# delete all content from server location
rm -Rf /var/www/raspberry/*
# copy raspberry folder to web server location
cp -R raspberry/ /var/www/
# copy production settings file
cp settings.py /var/www/raspberry/raspberry/
# collect django static files
/var/www/raspberry/manage.py collectstatic
# move custom admin files to the right folder
rm -Rf /var/www/raspberry/static/admin
mv /var/www/raspberry/admin /var/www/raspberry/static/
# set the right  permissions
chmod -R 755 /var/www/raspberry/

service apache2 restart
systemctl daemon-reload
