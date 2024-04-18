#!/bin/bash
set -ex
BINDIR=`dirname $0`
source $BINDIR/common.sh

if [ $# -eq 0 ] || [ $# -gt 1 ]; then
    echo "usage: $0 [dnn]"
    exit 1
fi
DNN=$1

echo "Configuring UE for DNN $DNN"

maybe_add_quectel_cm () {
    if ! test -f /etc/systemd/system/quectel-cm.service; then
        sudo cp $SERVICESDIR/quectel-cm.service /etc/systemd/system/quectel-cm.service
    fi
}

update_quectel_cm () {
    sudo sed -i "s/internet/$DNN/" /etc/systemd/system/quectel-cm.service
    sudo systemctl daemon-reload
    sudo systemctl restart quectel-cm.service
}

update_udhcpc_script () {
    sudo cp $BINDIR/default.script /etc/udhcpc/default.script
    sudo chmod +x /etc/udhcpc/default.script
}

install_iperf3 () {
    sudo apt install -y iperf3
}

maybe_add_quectel_cm
update_quectel_cm
update_udhcpc_script
install_iperf3
