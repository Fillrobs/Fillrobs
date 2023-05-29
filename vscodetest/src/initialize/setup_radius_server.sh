#!/bin/bash

echo "Setting up Radius Server"

read -p "FQDN or IP of RADIUS Server: " HOST
read -p "Port [1812]: " PORT
PORT=${PORT:-1812}
unset PASS
PASS_PROMPT="RADIUS Server secret: "
while IFS= read -p "$PASS_PROMPT"  -r -s -n 1 char
do
    if [[ $char == $'\0' ]]
    then
        break
    fi
    PASS_PROMPT='*'
    PASS="${PASS}${char}"
done
echo ""
echo "Select Auth Policy"
select AUTH_POLICY in "Token Only" "Token + Password" "Password + Token"
do
    echo ""
    break;
done

echo "Compiling RADIUS configurations for Execution..."

cat <<EOF > /tmp/radius_setup.py
from utilities.models import RADIUSUtility

def run_external_create_routines():
    """
    Wrapper for initializing items
    """

    auth_policy = "$AUTH_POLICY"
    if auth_policy == "Token + Password":
        auth_policy = "TOKEN+PIN"
    elif auth_policy == "Password + Token":
        auth_policy = "PIN+TOKEN"
    else:
        auth_policy = "TOKEN"

    RADIUS_UTILITY = {
        "secret": "$PASS",
        "server": "$HOST",
        "port": $PORT,
        "auth_policy": auth_policy
    }

    if RADIUSUtility.objects.exists():
        RADIUSUtility.objects.all().delete()

    radius = RADIUSUtility.objects.create(**RADIUS_UTILITY)



EOF

echo "Creating RADIUS Utility ..."
/opt/cloudbolt/initialize/create_objects.py /tmp/radius_setup.py

rm -f /tmp/radius_setup.py

echo "RADIUS configuration complete"
