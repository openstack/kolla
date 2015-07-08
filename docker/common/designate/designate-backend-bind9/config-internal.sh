#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh

check_required_vars DESIGNATE_MASTERNS DESIGNATE_SLAVENS DESIGNATE_BIND9_RNDC_KEY \
                    DESIGNATE_ALLOW_RECURSION

NAMEDCFG=/etc/named.conf

# /var/named is coming from a VOLUME definition but at first boot it needs to
# be populated from the original container since else it would be missing some
# Bind9 core files. These files have been saved during the build phase.

if [ ! -f /var/named/named.ca ]; then
    cp -pr /opt/kolla/var-named/* /var/named/
fi

# When rndc adds a new domain, bind adds the call in an nzf file in this
# directory.
chmod 770 /var/named
chown root:named /var/named

# Default Bind9 behavior is to enable recursion, disable if wanted.
if [ "${DESIGNATE_ALLOW_RECURSION}" == "false" ]; then
    sed -i -r "s/(recursion) yes/\1 no/" $NAMEDCFG
fi

sed -i -r "/listen-on port 53/d" $NAMEDCFG
sed -i -r "/listen-on-v6/d" $NAMEDCFG
sed -i -r "s,/\* Path to ISC DLV key \*/,allow-new-zones yes;," $NAMEDCFG
sed -i -r "/allow-query .+;/d" $NAMEDCFG

if ! grep -q rndc-key /etc/named.conf; then
    cat >> /etc/named.conf <<EOF
include "/etc/rndc.key";
controls {
    inet ${DESIGNATE_SLAVENS} allow { ${DESIGNATE_MASTERNS}; } keys { "rndc-key"; };
};
EOF
fi

cat > /etc/rndc.key <<EOF
key "rndc-key" {
    algorithm hmac-md5;
    secret "${DESIGNATE_BIND9_RNDC_KEY}";
};
EOF
cat > /etc/rndc.conf <<EOF
options {
    default-key "rndc-key";
    default-server 127.0.0.1;
    default-port 953;
};
EOF
cat /etc/rndc.key >> /etc/rndc.conf
chown named /etc/rndc.key

# Launch and keep in the foreground.
exec /usr/sbin/named -u named -g
