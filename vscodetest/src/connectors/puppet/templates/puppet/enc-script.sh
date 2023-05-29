#!/bin/sh

SITE_URL="{{ site_url }}"
PUPPET_CONF_ID={{ conf_id }}
NODE_NAME=$1

curl --fail ${SITE_URL}providers/puppet/${PUPPET_CONF_ID}/enc/${NODE_NAME}/
