prepare:
ifneq ($(and $(env)),)
	cp client_secrets.json /tmp/
	cp .${env}.env .env
	pip install -r requirements.txt
else
	@printf "provide the env variable. (env=local or env=prod)"
endif
