FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
RUN yum install -y which && \
    yum clean all

# See bug: https://bugs.launchpad.net/kolla/+bug/1483667
# TODO(SamYaple): Check in on this and remove once unneccesary
RUN pip install oslo.messaging==2.2.0

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
