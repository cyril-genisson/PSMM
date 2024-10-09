#!/usr/bin/env bash

PATH_USER="/home/monitor"
USERNAME="monitor"
KEY_PATH="$PATH_USER/.ssh"
KEY="$PATH_USER/.ssh/id_ed25519"
KEY_PUB="$PATH_USER/.ssh/id_ed25519.pub"

cp /home/vagrant/id_ed25519* $KEY_PATH/.

cat > script << EOF
#!/usr/bin/env bash
cd $PATH_USER
if [ ! -d env_monitor ]
then
    python3 -m venv env_monitor
    . env_monitor/bin/activate
    pip install mariadb paramiko sshtunnel requests
    deactivate
fi

if [ ! -d src ]
then
    mkdir src
fi

if [ ! -d bin ]
then
    mkdir bin
fi

EOF

chmod +x script
 
if [ -f $KEY ]
then
    chmod 600 $KEY_PATH/id_ed25519*
    chown $USERNAME:$USERNAME $KEY_PATH/id_ed25519*
fi

if [ ! -f /etc/apt/sources.list.d/mariadb.list ]
then
    curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
    apt update
    apt-get install -y pipx python3.11-venv python3-dev openssl libmariadb3 libmariadb-dev gcc python3-venv
    su $USERNAME -c ./script
fi

cp *.py $PATH_USER/src
cp *.json $PATH_USER/src
chown $USERNAME:$USERNAME $PATH_USER/src/*
chmod 700 $PATH_USER/src/*.py
sed -i "s/[[:cntrl:]]//g" $PATH_USER/src/*
