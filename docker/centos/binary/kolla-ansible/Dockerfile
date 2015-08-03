FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        git \
        gcc \
        libffi-devel \
        libxml2-devel \
        libxslt-devel \
        MySQL-python \
        openssl-devel \
        python-devel \
        openssh-clients \
    && yum clean all

RUN pip install -U pip wheel \
    && pip install python-openstackclient shade

RUN git clone https://github.com/ansible/ansible.git \
    && cd ansible \
    && git submodule update --init --recursive \
    && pip install .

RUN mkdir -p /etc/ansible /usr/share/ansible \
    && echo 'localhost ansible_connection=local' > /etc/ansible/hosts

COPY kolla_keystone_service.py kolla_keystone_user.py /usr/share/ansible/
