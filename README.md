# reciperadar

## Install dependencies

```
apt install \
  elasticsearch-oss \
  libpq-dev \
  pipenv \
  postgresql \
  rabbitmq-server
```

## Initialize the database
```
createuser <user>
createdb <user>
python -m reciperadar.services.database
```

## Initialize the search indices
```
pipenv shell
python scripts/reset-ingredient-index.py
python scripts/reset-recipe-index.py
```
