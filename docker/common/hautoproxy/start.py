#!/usr/bin/python

'''This script configures and starts a local haproxy instances, bound to
127.0.0.1, that forwards connections all of the discovered
docker/kubernetes environment variables.'''

import argparse
import os
import sys
from jinja2 import Environment, FileSystemLoader
import re
import urlparse

re_url = re.compile(
    '^(?P<name>.*)_PORT_(?P<port>\d+)_(?P<proto>(UDP|TCP))$')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--output', '-o',
                   default='/etc/haproxy/haproxy.cfg')
    p.add_argument('--no-start', '-n',
                   action='store_true')
    p.add_argument('--template-dir', '-t',
                   default='/etc/haproxy/templates')
    return p.parse_args()

def discover_services():
    services = []
    for k in os.environ:
        mo = re_url.match(k)

        if mo:
            parts = urlparse.urlparse(os.environ[k])
            remote_host,remote_port = parts.netloc.split(':')
            service_name = '%(name)s-%(port)s' % mo.groupdict()

            services.append({
                'remote_name': mo.group('name'),
                'remote_addr': remote_host,
                'remote_port': remote_port,
                'remote_proto': parts.scheme,
                'local_port': mo.group('port'),
                'service_name': service_name,
            })

    return services

def main():
    args = parse_args()
    services = discover_services()

    env = Environment(loader=FileSystemLoader(['.',
                                               args.template_dir]))
    template = env.get_template('haproxy.cfg.tmpl')
    with open(args.output, 'w') as fd:
        fd.write(template.render(services=services))

    if args.no_start:
        return

    os.execlp('haproxy', 'haproxy', '-f', args.output, '-db')

if __name__ == '__main__':
    main()

