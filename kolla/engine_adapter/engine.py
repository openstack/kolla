# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.version import StrictVersion
from enum import Enum
from kolla.image.utils import LOG

try:
    import docker
except (ImportError):
    LOG.debug("Docker python library was not found")


class Engine(Enum):

    DOCKER = "docker"


class UnsupportedEngineError(ValueError):

    def __init__(self, engine_name):
        super().__init__()
        self.engine_name = engine_name

    def __str__(self):
        return f'Unsupported engine name given: "{self.engine_name}"'


def getEngineException(conf):
    if conf.engine == Engine.DOCKER.value:
        return (docker.errors.DockerException)
    else:
        raise UnsupportedEngineError(conf.engine)


def getEngineClient(conf):
    if conf.engine == Engine.DOCKER.value:
        kwargs_env = docker.utils.kwargs_from_env()
        return docker.APIClient(version='auto', **kwargs_env)
    else:
        raise UnsupportedEngineError(conf.engine)


def getEngineVersion(conf):
    if conf.engine == Engine.DOCKER.value:
        return StrictVersion(docker.__version__)
    else:
        raise UnsupportedEngineError(conf.engine)
