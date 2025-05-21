#!/bin/bash
set -ex
BINDIR=`dirname $0`
source $BINDIR/common.sh



echo "Installing test tools"

install_ue_deps () {
    sudo apt update && sudo apt install -y --no-install-recommends \
      gpsd-clients \
      python3-pip
    sudo pip3 install -r $BINDIR/requirements.txt
}

install_ue_services () {
  python_scripts=$(ls $BINDIR/*.py)
  for script in $python_scripts; do
      sudo cp $script $SRCDIR
  done
  services=$(ls $SERVICESDIR/*.service)
  for service in $services; do
      sudo cp $service /etc/systemd/system
      sudo systemctl daemon-reload
      sudo systemctl enable $(basename $service)
      sudo systemctl restart $(basename $service)
  done
}

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://$ORCH_HOST:3100/loki/api/v1/push

scrape_configs:
- job_name: quectel-cm
  static_configs:
  - targets:
      - localhost
    labels:
      job: quectel-cm
      host: $HOSTNAME
      __path__: /var/log/quectel-cm.log
- job_name: ue-metrics
  static_configs:
  - targets:
      - localhost
    labels:
      job: ue-metrics
      host: $HOSTNAME
      __path__: /var/log/ue-metrics.log
- job_name: gps
  static_configs:
  - targets:
      - localhost
    labels:
      job: gps
      host: $HOSTNAME
      __path__: /var/log/gps.log
EOF
    sudo cp /tmp/promtail-config.yml /etc/promtail/config.yml
}

install_ue_deps
install_ue_services
