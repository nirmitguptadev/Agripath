@echo off
echo Running Django tests...
python manage.py test tests --verbosity=2
pause