ssh: ## Create SSH connection to RPi
	@ssh pi@${SSH_ADDRESS}

install-direnv: ## Install DirEnv terminal environment variable manager
	@curl -sfL https://direnv.net/install.sh | bash

install-bcm2835: ## Install bcm2835 dependency
	@wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz && \
	tar zxvf bcm2835-1.71.tar.gz && \
	cd bcm2835-1.71/ && \
	sudo ./configure && sudo make && \
	sudo make check && \
	sudo make install

install-wiringpi: ## Install WiringPi dependency (outputted version should be v2.70)
	@git clone https://github.com/WiringPi/WiringPi && \
	cd WiringPi && \
	./build && \
	gpio -v

install-pyenv: ## Install PyEnv and Python 3.9.18
	@curl https://pyenv.run | bash && \
	pyenv install 3.9.18

install-poetry: ## Activate Python 3.9.18 and install Poetry
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	curl -sSL https://install.python-poetry.org | python3 -

install-rust: ## Install Rust (to build pyopensll dependency)
	@curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

poetry-install-rpi: ## Activate Python 3.9.18 and install Poetry-managed dependencies for RPi usage
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	poetry config virtualenvs.in-project true && \
	echo "Installing pillow build dependencies.." && \
	sudo apt-get update && \
	sudo apt-get install libjpeg-dev -y && \
	sudo apt-get install zlib1g-dev -y && \
	sudo apt-get install libfreetype6-dev -y && \
	sudo apt-get install libopenjp2-7 -y && \
	sudo apt-get install libtiff5 -y && \
	sudo apt-get install libssl-dev && \
	echo "Initialising Poetry environment.." && \
	poetry install --with rpi

poetry-install-local-dev: ## Activate Python 3.9.18 and install code development dependencies for locla PC development (not on RPi)
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	poetry config virtualenvs.in-project true && \
	echo "Initialising Poetry environment.." && \
	poetry install --without rpi

make poetry-install-all:
	@make poetry-install-rpi

install-all: ## Run all install steps in correct order
	@install-direnv && \
	make install-bcm2835 && \
	make install-wiringpi && \
	make install-pyenv && \
	make install-poetry && \
	make install-rust && \
	make poetry-install-all

test-install: ## Run a test-suite to verify installation
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	echo "TODO: write installation test"

run: ## Run main app
	@poetry run python3 spotify_e_paper_control/main.py

generate-ssl-cert: ## Generate an OpenSSL certificate & key to enable HTTPS
	@cd spotify_e_paper_control/ssl && \
	openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365