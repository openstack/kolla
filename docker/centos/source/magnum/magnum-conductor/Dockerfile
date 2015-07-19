FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%magnum-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install kubectl binary (ugh)
RUN cd /tmp && curl -L https://github.com/GoogleCloudPlatform/kubernetes/releases/download/v0.15.0/kubernetes.tar.gz -o /tmp/kubernetes.tar.gz && /usr/bin/tar -xzvf /tmp/kubernetes.tar.gz && cp -a /tmp/kubernetes/platforms/linux/amd64/kubectl /usr/bin/kubectl && rm -rf /tmp/kubernetes

COPY ./start.sh /start.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
