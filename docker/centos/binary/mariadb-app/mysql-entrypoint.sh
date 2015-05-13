#!/bin/bash
set -e

# Configure MySQL settings
. /opt/kolla/config-mysql.sh

if [ -z "$(ls -A /var/lib/mysql)" -a "${1%_safe}" = 'mysqld' ]; then
        PATH=/usr/libexec:$PATH
        export PATH

        if [ -z "$MARIADB_ROOT_PASSWORD" ]; then
                echo >&2 'error: database is uninitialized and MARIADB_ROOT_PASSWORD not set'
                echo >&2 '  Did you forget to add -e MARIADB_ROOT_PASSWORD=... ?'
                exit 1
        fi

        mysql_install_db --user=mysql --datadir="$DATADIR"

        # These statements _must_ be on individual lines, and _must_ end with
        # semicolons (no line breaks or comments are permitted).
        # TODO proper SQL escaping on ALL the things D:
        TEMP_FILE='/tmp/mysql-first-time.sql'
        cat > "$TEMP_FILE" <<-EOSQL
		DELETE FROM mysql.user ;
		CREATE USER 'root'@'%' IDENTIFIED BY '${MARIADB_ROOT_PASSWORD}' ;
		GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION ;
		DROP DATABASE IF EXISTS test ;
	EOSQL

        if [ "$MARIADB_DATABASE" ]; then
                echo "CREATE DATABASE IF NOT EXISTS $MARIADB_DATABASE ;" >> "$TEMP_FILE"
        fi

        if [ "$MARIADB_USER" -a "$MARIADB_PASSWORD" ]; then
                echo "CREATE USER '$MARIADB_USER'@'%' IDENTIFIED BY '$MARIADB_PASSWORD' ;" >> "$TEMP_FILE"

                if [ "$MARIADB_DATABASE" ]; then
                        echo "GRANT ALL ON $MARIADB_DATABASE.* TO '$MARIADB_USER'@'%' ;" >> "$TEMP_FILE"
                fi
        fi

        echo 'FLUSH PRIVILEGES ;' >> "$TEMP_FILE"

        set -- "$@" --init-file="$TEMP_FILE"
fi

chown -R mysql:mysql "$DATADIR"

exec "$@"
