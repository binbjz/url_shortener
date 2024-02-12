# URL Shortener Service with FastAPI、MongoDB and Pytest

## Build the image and run the container:

```sh
$ docker-compose up -d --build
```

## Update the image and run unit test:

```sh
$ docker-compose exec web pytest .
```

Test out the following routes:

1. [http://localhost:8002/](http://localhost:8002/)
1. [http://localhost:8002/docs](http://localhost:8002/docs)
1. [http://localhost:8002/api/v1/shorten](http://localhost:8002/api/v1/shorten)
1. [http://localhost:8002/api/v1/shorten/batch](http://localhost:8002/api/v1/shorten/batch)
1. [http://localhost:8002/api/v1/shorten/batch_conc](http://localhost:8002/api/v1/shorten/batch_conc)
1. [http://localhost:8002/api/v1/{short_url}](http://localhost:8002/api/v1/{short_url})
1. [http://localhost:8002/api/v1/urls/delete/{short_url}](http://localhost:8002/api/v1/urls/delete/{short_url})
1. [http://localhost:8002/test-delete](http://localhost:8002/test-delete)
