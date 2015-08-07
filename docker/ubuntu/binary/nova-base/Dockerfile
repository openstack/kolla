FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN apt-get install -y --no-install-recommends \
        nova-common \
        python-cinderclient \
        python-keystoneclient \
        python-nova \
        bridge-utils \
    && apt-get clean
