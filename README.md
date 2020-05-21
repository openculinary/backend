# RecipeRadar API

The RecipeRadar API provides services to the RecipeRadar [frontend](https://www.github.com/openculinary/frontend) and [crawler](https://www.github.com/openculinary/crawler) applications.

It provides endpoints to support the following functionality:

* Recipe and ingredient search
* User feedback collection
* Recipe crawling (cluster-internal)
* Data export (cluster-internal)

The service is composed of two Kubernetes deployments:

* `api-deployment` - `gunicorn` web pods
* `api-worker-deployment` - `celery` task workers

The `api-deployment` component has high uptime and availability requirements since it's a core part of the [frontend](https://www.github.com/openculinary/frontend) recipe search experience.

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](https://www.github.com/openculinary/infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```sh
$ pipenv install --dev
$ make lint tests
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```sh
$ make
$ make deploy
```

## Operations

### Recipe index configuration

For the search engine to correctly index recipe data, an Elasticsearch mapping needs to be configured for the `recipe` index.  This can be done using the `update-recipe-index.py` script:

```sh
# For an Elasticsearch instance running on 'localhost' on the default port
$ pipenv run python scripts/update-recipe-index.py --hostname localhost
```

### Pausing background workers

Sometimes -- for example, during schema upgrades or other changes which need careful co-ordination between the search engine, API, and background task workers, it can be useful to pause the workers temporarily.

Since the workers are a Kubernetes `deployment`, a straightforward way to do this is to scale the deployment down to zero temporarily:

```sh
$ kubectl scale deployments/api-worker-deployment --replicas 0
```
