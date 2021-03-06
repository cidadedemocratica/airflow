up:
ifneq ($(and $(env)),)
	env=${env} docker-compose up -d
else
	@printf "provide the env variable. (env=local or env=prod)"
endif

build:
	docker-compose build --no-cache

run:
ifneq ($(and $(env)),)
	env=${env} docker-compose build
	env=${env} docker-compose up -d
else
	@printf "provide the env variable. (env=local or env=prod)"
endif
