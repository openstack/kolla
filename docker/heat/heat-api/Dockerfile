FROM kollaglue/fedora-rdo-heat-base
MAINTAINER Jeff Peeler <jpeeler@redhat.com>

# TODO: configure cfn and cloudwatch
# TODO: remove python-openstackclient once crux feature is added in start.sh
RUN yum -y install \
    openstack-heat-api \
    python-openstackclient \
    ; yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
