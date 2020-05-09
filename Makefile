run:
ifneq ($(and $(env)),)
	env=${env} docker-compose build
	env=${env} docker-compose up
else
	@printf "provide the env variable. (env=local or env=prod)"
endif
