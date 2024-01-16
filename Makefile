ssh: ## Create SSH connection to RPi
	@ssh pi@${SSH_ADDRESS}

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

install-python-deps: ## Activate Python 3.9.18 and install Numpy, Pillow, RPi.GPIO and Spidev
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	sudo apt-get update && \
	sudo apt-get install python3-pil && \
	sudo apt-get install python3-numpy && \
	sudo pip3 install RPi.GPIO && \
	sudo pip3 install spidev

install-poetry: ## Activate Python 3.9.18 and install Poetry
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	curl -sSL https://install.python-poetry.org | python3 -

install-poetry-deps: ## Activate Python 3.9.18 and install Poetry-managed dependencies
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	poetry config virtualenvs.in-project true && \
	poetry install

install-all: ## Run all install steps in correct order
	@make install-bcm2835 && \
	make install-wiringpi && \
	make install-pyenv && \
	make install-python-deps && \
	make install-poetry && \
	make install-poetry-deps

test-install: ## Run a test-suite to verify installation
	@pyenv local 3.9.18 && \
	echo "Using `pyenv local`.." && \
	echo "todo"