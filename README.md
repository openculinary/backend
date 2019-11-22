# RecipeRadar API

The RecipeRadar API provides services to the RecipeRadar [frontend](../frontend) and [crawler](../crawler) applications.

It provides endpoints to support the following functionality:

* Recipe and ingredient search
* User feedback collection
* Recipe crawling (cluster-internal)
* Data export (cluster-internal)

The service is composed of two Kubernetes deployments:

* `api-deployment` - `gunicorn` web pods
* `api-worker-deployment` - `celery` task workers

The `api-deployment` component has high uptime and availability requirements since it's a core part of the [frontend](../frontend) recipe search experience.

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](../infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```
pipenv install --dev
pipenv run make
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```
sudo sh -x ./build.sh
sh -x ./deploy.sh
```

## Operations

### Recipe index configuration

For the search engine to correctly index recipe data, an Elasticsearch mapping needs to be configured for the `recipe` index.  This can be done using the `update-recipe-index.py` script:

```
# For an Elasticsearch instance running on 'localhost' on the default port
pipenv run python scripts/update-recipe-index.py --hostname localhost
```

### Pausing background workers

Sometimes -- for example, during schema upgrades or other changes which need careful co-ordination between the search engine, API, and background task workers, it can be useful to pause the workers temporarily.

Since the workers are a Kubernetes `deployment`, a straightforward way to do this is to scale the deployment down to zero temporarily:

```
kubectl scale deployments/api-worker-deployment --replicas 0
```
