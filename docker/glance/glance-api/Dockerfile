FROM kollaglue/fedora-rdo-glance-base
MAINTAINER Dan Radez <dradez@redhat.com>

VOLUME /var/lib/glance

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
