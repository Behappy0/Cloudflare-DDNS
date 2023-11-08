# Cloudflare-DDNS

A DDNS service using cloudflare api.

## Install

> **Prerequests:** cloudflare api token with zone dns read/write permit.

### with pip

Install python package:

```shell
pip install https://github.com/Behappy0/Cloudflare-DDNS/archive/master.zip
```

Run service:

```shell
cloudflare-ddns -n "your_host_name" -d "your_domain_name" -k $"your_cloudflare_token" -t "your_dns_record_type"
```

Run service in the background:

```shell
nohup cloudflare-ddns -n "your_host_name" -d "your_domain_name" -k $"your_cloudflare_token" -t "your_dns_record_type" &
```

More information about command line arguments can be seen [here](#command-line-arguments).

### with docker(recommend)

Build docker image:

```shell
git clone https://github.com/Behappy0/Cloudflare-DDNS.git
cd ./Cloudflare-DDNS/docker
docker build -t cloudflare-ddns .
```

Run container by docker cli:

```shell
docker run -d \
    --name Cloudflare-DDNS \
    --restart unless-stopped \
    -e HOST_NAME=your_host_name \
    -e DOMAIN_NAME=your_domain_name \
    -e TOKEN=your_cloudflare_token \
    -e TYPE=your_dns_record_type \
    cloudflare-ddns
```

Run container by docker-compose:

```shell
# edit compose file
vim docker-compose.yaml

# run
docker-compose up -d
```

More information about docker envirnoment variables can be seen [here](#docker-envirnoment-variables).

## Uninstall

### with pip

```shell
pip uninstall cloudflare-ddns
```

### with docker

```shell
docker stop Cloudflare-DDNS
docker rm Cloudflare-DDNS
docker rmi cloudflare-ddns
```

## Command Line Arguments

## Docker Envirnoment Variables
