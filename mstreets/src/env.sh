#/usr/bin/python3
ENVNAME=".env"

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
export ENVIRONMENT_NAME=devel

if [ -d $ENVNAME ]; then

    alias run="python manage.py runserver"
    alias migrate="python manage.py migrate"
    alias makemigrations="python manage.py makemigrations"
    . $ENVNAME/bin/activate

else

    virtualenv $ENVNAME --python=python3
    . $ENVNAME/bin/activate
    pip install -r requirements-devel.txt

fi
