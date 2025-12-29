@echo off
mkdir myproject 2>nul
cd myproject

python -m venv env
call env\Scripts\activate

python -m pip install django 
python -m pip install django-taggit markdown
python -m pip install django-autoslug
python -m pip install pytils

django-admin startproject mysite .
python manage.py startapp blog

python -c "with open('mysite/settings.py', encoding='utf-8') as f: t = f.read(); t = t.replace('INSTALLED_APPS = [', 'INSTALLED_APPS = [\n    \"blog.apps.BlogConfig\",\n    \"taggit\",'); with open('mysite/settings.py', 'w', encoding='utf-8') as f: f.write(t)"

python manage.py migrate

echo from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin123') if not User.objects.filter(username='admin').exists() else None | python manage.py shell

echo Success. Run: py manage.py runserver
pause