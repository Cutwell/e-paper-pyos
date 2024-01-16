<!-- Update this link with your own project logo -->
# <img src="https://raw.githubusercontent.com/Cutwell/spotify-e-paper-control/main/logo.png" style="width:64px;padding-right:20px;margin-bottom:-8px;"> Spotify E-Paper Control
 Control Spotify playback on other devices using a touchscreen e-paper device.

<!-- Find new badges at https://shields.io/badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/readme-template-cli)](https://pypi.org/project/readme-template-cli/)

- Control Spotify playback from a touchscreen e-paper device.
- Plug-and-play compatability with the [Waveshare 2.13" Touch E-paper Hat](https://www.waveshare.com/2.13inch-touch-e-paper-hat.htm) and [Raspberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).


## Setup

### Shortcut for connecting to RPI with SSH

1. Create `.envrc` with `SSH_ADDRESS` environment variable (also store `SSH_PASSWD` for future reference).
2. Add variables to terminal environment with `direnv allow`.
3. Create an SSH session using `make ssh`

### Installation

_Requirements_:

1. [PyEnv](https://github.com/pyenv/pyenv) and Python 3.9.18:

```sh
curl https://pyenv.run | bash
pyenv install 3.9.18
```

_❗ Note: If you're having installation issues, [make sure your build environment is set up correctly](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)._

2. Setup your RPI using the [WaveShare documentation](https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT_Manual#Raspberry_Pi). Python module requirements are managed via Poetry:

Install depencendies:

```sh
poetry install
poetry run python -m pip install RPi.GPIO spidev
```

## Contributing

<!-- Remember to update the links in the `.github/CONTRIBUTING.md` file from `Cutwell/spotify-e-paper-control` to your own username and repository. -->

For information on how to set up your dev environment and contribute, see [here](.github/CONTRIBUTING.md).

## License

MIT
