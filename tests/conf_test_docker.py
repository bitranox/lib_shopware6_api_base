# Configuration for the dockware Docker test container.
#
# For testing we use the dockware docker container.
# See: https://developer.shopware.com/docs/guides/installation/dockware
#
# On GitHub Actions the dockware container is installed as a service
# and is available for communication on localhost.
#
# Start the dockware container locally with:
#   docker run -d --rm -p 80:80 --name dockware dockware/dev:latest

# STDLIB
from pathlib import Path

# conf
from lib_shopware6_api_base.conf_shopware6_api_base_classes import ConfShopware6ApiBase

# Load configuration from docker.env file located next to this module
_docker_env_file = Path(__file__).parent / "docker.env"

conf_shopware6_api_base = ConfShopware6ApiBase.from_env_file(_docker_env_file)
