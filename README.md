# reciperadar

## Install dependencies

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt install \
  elasticsearch-oss \
  libpq-dev \
  pipenv \
  postgresql \
  rabbitmq-server
```

## Initialize the database
```
sudo -u postgres createuser <user>
sudo -u postgres createdb <user>
python -m reciperadar.services.database
```

## Initialize the search indices
```
pipenv shell
python scripts/reset-recipe-index.py
```
