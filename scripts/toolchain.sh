
## Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

## Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

## Install Python 3.13
uv install python 3.13

## Install Ruff
uv tool install ruff

## Setup pnpm via corepack
npm install --global corepack@latest
corepack use pnpm@latest-11
