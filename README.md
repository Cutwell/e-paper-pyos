<!-- Update this link with your own project logo -->
# <img src="https://raw.githubusercontent.com/Cutwell/e-paper-pyos/main/logo.png" style="width:64px;padding-right:20px;margin-bottom:-8px;"> E-Paper PyOS
 Python-based operating system for touchscreen e-paper devices.

<!-- Find new badges at https://shields.io/badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- A Python-based OS for e-paper applications.
	- e.g.: Spotify playback control
- Plug-and-play compatability with the [Waveshare 2.13" Touch E-paper Hat](https://www.waveshare.com/2.13inch-touch-e-paper-hat.htm) and [Raspberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).


## Setup

Follow this guide to setup your Raspberry Pi Zero 2W and Waveshare 2.13" Touch E-paper Hat:

1. Follow [this](https://developer.spotify.com/documentation/web-api/tutorials/getting-started#create-an-app) Spotify guide to create an app.
2. Create `.envrc`, using `.envrc.example.sh` as a template, and add your client ID/secret, etc.
3. Install [direnv](https://direnv.net/) with `make install-direnv`.
3. Access variables in your terminal environment with `direnv allow`.

_❗ Developer note: Try using `make ssh` as a shortcut to connect to your RPi._

### Installation

1. Setup your RPi using the [WaveShare documentation](https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT_Manual#Raspberry_Pi). Follow the guide until `Libraries Installation`, then follow the steps below:

2. Install dependencies and libraries..

On a fresh Raspberry Pi:

```sh
make install-all
```

Install dependencies selectively:

|Dependency||
|:---:|:---:|
|[BCM2835](https://www.airspayce.com/mikem/bcm2835/) (RPi Broadcom chip) C library|`make install-bcm2835`|
|[WiringPi](https://github.com/WiringPi/WiringPi) C library|`make install-wiringpi`|
|[Rust](https://www.rust-lang.org/tools/install) (to install [PyOpenSSL](https://pypi.org/project/pyOpenSSL/))|`make install-rust`|
|[PyEnv](https://github.com/pyenv/pyenv) & [Python 3.9.18](https://www.python.org/downloads/release/python-3918/)|`make install-pyenv`|
|[Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)|`make install-poetry`|
|Poetry-managed Python dependencies|`make install-poetry-deps`|

_❗ Note: If you're having issues installing PyEnv, [make sure your build environment is set up correctly](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)._

_❗ Note: Certain e-paper apps require you to login to services on your phone by scanning QR codes. Login tokens are then shared with the e-paper via callback to the devices `.local` presence on your local network. If your device defaults to HTTPS, you will need to generate an OpenSSL certificate for app servers, using `make generate-ssl-cert`._

3. Test your installation was successful by running:

```sh
make test-install
```

### Troubleshooting

The following dependencies might be missing from your system:

```sh
sudo apt-get install liblcms1-dev -y
```

## Contributing

<!-- Remember to update the links in the `.github/CONTRIBUTING.md` file from `Cutwell/e-paper-pyos` to your own username and repository. -->

For information on how to set up your dev environment and contribute, see [here](.github/CONTRIBUTING.md).

## License

MIT
