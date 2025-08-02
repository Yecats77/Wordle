# Wordle

## backend

port 7364

```bash
conda create --name wordle
conda activate wordle
conda install python
conda install django
django-admin startproject wordle_api
pip install djangorestframework
pip install django-cors-headers
pip install django-crontab
pip install psycopg2
pip install django-filter django-extensions
django-admin startapp game
python manage.py runserver 7364
```

postgresql

```bash
sudo service postgresql start
sudo -u postgres createdb wordledb
sudo -u postgres psql
```

```sql
alter user postgres with encrypted password 'password';
grant all privileges on database wordledb to postgres;
\q
```

## frontend

port 7368

```bash
sudo npm install -g @vue/cli
vue create wordle_web
npm install axios
sudo apt install vite
npm install vite@latest
npm install naive-ui
npm install antd @types/antd
npm install
npm run dev

npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```
