# RecipeRadar Backend

The RecipeRadar backend provides data persistence and modeling services.

It provides endpoints to support the following functionality:

* Recipe crawling
* Data export

The service is composed of two Kubernetes deployments:

* `backend-deployment` - `gunicorn` web pods
* `backend-worker-deployment` - `celery` task workers

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](https://www.github.com/openculinary/infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```sh
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

For the search engine to correctly index recipe data, an OpenSearch mapping needs to be configured for the `recipe` index.  This can be done using the `update-recipe-index.py` script:

```sh
# For an OpenSearch instance running on 'localhost' on the default port
$ venv/bin/python scripts/update-recipe-index.py --hostname localhost --index recipes
```

### Pausing background workers

Sometimes -- for example, during schema upgrades or other changes which need careful co-ordination between the search engine, API, and background task workers, it can be useful to pause the workers temporarily.

Since the workers are a Kubernetes `deployment`, a straightforward way to do this is to scale the deployment down to zero temporarily:

```sh
$ kubectl scale deployments/backend-worker-deployment --replicas 0
```
