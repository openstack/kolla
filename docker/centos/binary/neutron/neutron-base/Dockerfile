FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-neutron \
                   openstack-neutron-ml2 \
                   python-neutron-client \
    && yum clean all

RUN mkdir -p /opt/kolla/host_proc

RUN pip install nsenter \
    && ln -s 1 /opt/kolla/host_proc/self

COPY config-neutron.sh config-sudoers.sh /opt/kolla/

RUN mv /sbin/ip /opt/kolla/ip
COPY ip_wrapper.py /sbin/ip
