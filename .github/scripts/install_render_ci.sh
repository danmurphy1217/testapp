#/bin/bash
set -eo pipefail

export RENDER_VERSION="v0.1.0"

wget https://github.com/gruntwork-io/fetch/releases/download/v0.4.6/fetch_linux_amd64
sudo mv fetch_linux_amd64 /usr/local/bin/fetch
sudo chmod +x /usr/local/bin/fetch

fetch --repo="https://github.com/ComunHQ/render" --tag=$RENDER_VERSION --release-asset='render-amd64-linux' .
sudo mv render-amd64-linux /usr/local/bin/render 
sudo chmod +x /usr/local/bin/render

test render
