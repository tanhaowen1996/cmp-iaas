
tag=latest
registry_host=10.209.0.121:5000


all: build_image

build_image:
	docker build . -f Dockerfile -t yh/cmp-iaas:${tag}


push: push-cmp-iaas-dev

push-cmp-iaas-dev:
	docker tag yh/cmp-iaas:${tag} ${registry_host}/yh/cmp-iaas:${tag}
	docker push ${registry_host}/yh/cmp-iaas:${tag}

