FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:latest
MAINTAINER michal.stachowski@intel.com

RUN yum install -y openvswitch
ADD ./start.sh /start.sh
CMD ["/start.sh"]
