FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./start.sh /start.sh

# Install required packages
RUN yum install -y gcc Cython sqlite-devel mysql-devel libffi-devel && yum clean all

# use the Barbican Juno version
# setting this as environment variable also keeps pbr version checking happy
# TODO: when the Barbican rpm from cloudkeep.io is usable,
# switch to using that instead
ENV PBR_VERSION 2014.2

# Get and extract the Barbican tar ball
RUN curl -o /barbican-$PBR_VERSION.tar.gz https://github.com/openstack/barbican/archive/$PBR_VERSION.tar.gz -L
RUN tar -xzf barbican-$PBR_VERSION.tar.gz

# Install Barbican requirements
RUN pip install -r barbican-$PBR_VERSION/requirements.txt
RUN pip install MySQL-python

# Install Barbican
RUN cd barbican-$PBR_VERSION && python setup.py install

# Configure Barbican
RUN mkdir -p /etc/barbican
RUN mkdir -p /var/log/barbican
RUN cp -r /barbican-$PBR_VERSION/etc/barbican/* /etc/barbican

# Instal uwsgi as that is what we will use to run Barbican
RUN pip install uwsgi

# Cleanup files not required anymore
RUN rm -rf /barbican-$PBR_VERSION
RUN rm -rf /barbican-$PBR_VERSION.tar.gz

CMD ["/start.sh"]
