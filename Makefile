ssh:
	@ssh pi@${SSH_ADDRESS}

install:
	@poetry config virtualenvs.in-project true \
	&& poetry install