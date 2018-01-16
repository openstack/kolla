#!/usr/bin/python2
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import glob
import logging
import os
import re
import sys

import rrdtool


LOG = logging.getLogger('root')

COLORS = (
    '#0000ff',
    '#00ff00',
    '#ff0000',
    '#00ffff',
    '#ffff00',
    '#ff00ff'
)


def colorgen():
    for color in COLORS:
        yield color


def get_uptime_seconds():
    with open('/proc/uptime') as f:
        return f.read().split(' ')[0]


class LoadGraph(object):

    DEF = 'DEF:%(vname)s=%(filename)s:%(ds)s:%(CF)s'
    LINE = 'LINE1:%(vname)s%(color)s:%(vname)s'
    AREA = 'AREA:%(vname)s%(color)s:%(vname)s'

    def __init__(self, conf, file, color):
        self.conf = conf
        self.color = colorgen()
        self.file = file
        self.info = RRDInfo(file)
        self.color = color
        self.filename = os.path.basename(self.file)

    def _gen_line(self, vname, ds, color):
        params = dict(vname=vname,
                      ds=ds,
                      filename=self.file,
                      color=color,
                      CF=self.conf.cf)
        ret = []
        ret.append(self.DEF % params)
        draw = self.LINE
        if self.conf.area:
            draw = self.AREA
        if self.conf.stack:
            draw += ':STACK'
        ret.append(draw % params)
        LOG.info('Get params for ds: %s', ret)
        return ret

    def gen_params(self):

        ret = []
        for DS in self.info.data_sources():
            filename, ext = os.path.splitext(self.filename)
            vname = '%s-%s' % (filename, DS)
            ret.extend(self._gen_line(vname, DS, next(self.color)))
        return ret

    def graph(self):
        params = self.common_params()
        params += self.get_period()
        params.extend(self.gen_params())
        return rrdtool.graphv(*params)


class RRDInfo(object):

    def __init__(self, file):
        self.info = rrdtool.info(file)

    @property
    def last_update(self):
        return self.info['last_update']

    def data_sources(self):
        dss = set()
        for key in self.info:
            ds = re.findall('ds\[(\w*)', key)
            if ds:
                dss.add(ds[0])
        return dss


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', nargs='+')
    parser.add_argument('--type')
    parser.add_argument('--height', default='256')
    parser.add_argument('--width', default='1024')
    parser.add_argument('--output', default='a.png')

    parser.add_argument('--stack', action='store_true')
    parser.add_argument('--area', action='store_true')
    parser.add_argument('--cf', default='MAX')

    parser.add_argument('--start', default=None)
    parser.add_argument('--end', default=None)

    conf = parser.parse_args(sys.argv[1:])

    last_update = None

    rrd_definitions = []

    color = colorgen()

    rrd_files = []
    for f in conf.file:
        f = os.path.expanduser(f)
        rrd_files.extend(glob.glob(f))
    LOG.info('Get rrdfiles: %s', rrd_files)

    for file in rrd_files:
        rrd_definitions.extend(LoadGraph(conf, file, color=color).gen_params())
        if not last_update:
            last_update = RRDInfo(file).last_update
        else:
            last_update = min(RRDInfo(file).last_update, last_update)

    start = conf.start
    end = conf.end
    if not start:
        start = 'end-' + get_uptime_seconds()
    if not end:
        end = str(last_update + 60)

    params = [
        conf.output,
        '--zoom', '4',
        '--width', conf.width,
        '--height', conf.height,
        '--start', start,
        '--end', end
        ]
    params.extend(rrd_definitions)
    LOG.debug('params: %s', params)

    rrdtool.graph(*params)


if __name__ == "__main__":
    main()
