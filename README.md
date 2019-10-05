# reciperadar

## Install dependencies

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo 'deb https://artifacts.elastic.co/packages/oss-7.x/apt stable main' | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt install \
  elasticsearch-oss \
  libpq-dev \
  pipenv \
  postgresql \
  rabbitmq-server
```

## Initialize the database
```
sudo -u postgres createuser api
sudo -u postgres createdb api

pipenv run python -m reciperadar.services.database
```

## Initialize the search indices
```
pipenv run python scripts/reset-recipe-index.py
```
