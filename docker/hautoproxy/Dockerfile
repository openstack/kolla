FROM fedora

RUN yum -y install haproxy python-jinja2; yum clean all
RUN mkdir -p /etc/haproxy/templates
ADD haproxy.cfg.tmpl /etc/haproxy/templates/haproxy.cfg.tmpl
ADD start.py /start.py
CMD ["/start.py"]

