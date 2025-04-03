#!/bin/bash
set -e

# Detect IP address and set environment variables
export IP_ADDRESS=$(hostname -I | awk '{print $1}')
export DU_FQDN="pcd.pf9.io"
export REGION_NAME="Community"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Spinner function
if [[ $- == *x* ]]; then
    # For debug mode that shows all output
    run_with_spinner() {
        local message="$1"
        local commands="$2"
        echo "$message... processing"
        eval "$commands"
        local exit_status=$?

        if [ $exit_status -eq 0 ]; then
            echo " ${GREEN}Done${NC}"
        else
            echo " ${RED}Failed${NC}"
            exit $exit_status
        fi
    }
else
    # For normal operation
    run_with_spinner() {
        local message="$1"
        local commands="$2"

        echo -n "$message... "
        (eval "$commands") > /dev/null 2>&1 &
        local pid=$!

        # Simple blinking spinner
        while kill -0 $pid 2>/dev/null; do
            echo -ne "${RED}▓${NC}"
            sleep 0.5
            echo -ne "\b${RED}▒${NC}"
            sleep 0.5
            echo -ne "\b"
        done

        # Wait for process to finish and check its exit status
        wait $pid
        local exit_status=$?

        # Print done or failed based on exit status
        if [ $exit_status -eq 0 ]; then
            echo -e " ${GREEN}Done${NC}"
        else
            echo -e " ${RED}Failed${NC}"
            # Run the command again to display the error
            eval "$commands"
            exit $exit_status
        fi
    }
fi

echo "Private Cloud Director Community Edition Deployment Started..."

# Stable version
run_with_spinner "Finding latest version" "
    mkdir -p \${HOME}/pcd-ce &&
    cd \${HOME}/pcd-ce &&
    curl -O https://pcd-community.s3-accelerate.amazonaws.com/stable.txt
"

export VERSION=$(cat $HOME/pcd-ce/stable.txt)

# Download PCD CE artifacts
run_with_spinner "Downloading artifacts" "
    mkdir -p \${HOME}/pcd-ce &&
    cd \${HOME}/pcd-ce &&
    curl --silent https://pcd-community.s3-accelerate.amazonaws.com/\$VERSION/index.txt |
    grep -e airctl -e install-pcd.sh -e nodelet-deb.tar.gz -e nodelet.tar.gz -e pcd-chart.tgz -e options.json -e version.txt -e helm |
    awk -v ver=\"\$VERSION\" '{print \"curl -sS \\\"https://pcd-community.s3-accelerate.amazonaws.com/\" ver \"/\" \$NF \"\\\" -o \${HOME}/pcd-ce/\" \$NF}' |
    bash
"

# Set system configurations
run_with_spinner "Setting some configurations" "
    sudo sysctl -w fs.inotify.max_queued_events=512000 &&
    sudo sysctl -w fs.inotify.max_user_instances=512000 &&
    sudo sysctl -w fs.inotify.max_user_watches=512000 &&
    sudo sysctl -w fs.aio-max-nr=500000
"

# Install PCD CE artifacts, modify options, and install kubectl
run_with_spinner "Installing artifacts and dependencies" "
    cd ${HOME}/pcd-ce &&
    chmod +x ./install-pcd.sh &&
    ./install-pcd.sh ${VERSION} &&
    sudo cp /opt/pf9/airctl/airctl /usr/bin/ &&
    echo 'export PATH=\$PATH:/opt/pf9/airctl' >> ~/.bashrc &&
    . ~/.bashrc &&
    sed -i 's/\"skip_components\": \"\"/\"skip_components\": \"gnocchi\"/g' /opt/pf9/airctl/conf/options.json &&
    sed -i 's/\"community_edition\": \"false\"/\"community_edition\": \"true\"/g' /opt/pf9/airctl/conf/options.json &&
    curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\" &&
    chmod +x kubectl &&
    sudo mv kubectl /usr/local/bin/
"

# Configure Airctl
run_with_spinner "Configuring Airctl" "
    airctl configure --unattended --cluster-deployment-type k3s --du-fqdn \$DU_FQDN --ipv4-enabled --master-ips \$IP_ADDRESS --external-ip4 \$IP_ADDRESS --regions \$REGION_NAME --storage-provider hostpath-provisioner
"

# Create K8s cluster
run_with_spinner "Creating K8s cluster" "airctl create-cluster --config /opt/pf9/airctl/conf/airctl-config.yaml --verbose"

# Start PCD CE Environment
run_with_spinner "Starting PCD CE environment (this will take approx 45 mins)" "airctl start --config /opt/pf9/airctl/conf/airctl-config.yaml --verbose"

echo "Private Cloud Director Community Edition Deployment Completed!"
echo ""

# Get credentials and show output
BASE=$(echo $DU_FQDN | cut -d. -f1)
DOMAIN=$(echo $DU_FQDN | cut -d. -f2-)
BASE_LC=$(echo $BASE | tr '[:upper:]' '[:lower:]')
REGION_LC=$(echo $REGION_NAME | tr '[:upper:]' '[:lower:]')
DOMAIN_LC=$(echo $DOMAIN | tr '[:upper:]' '[:lower:]')

echo "Login Details:"
echo "FQDN: $BASE_LC-$REGION_LC.$DOMAIN_LC"
airctl get-creds --config /opt/pf9/airctl/conf/airctl-config.yaml

echo ""
echo "Note: If internal DNS is unavailable, add the management plane FQDN to /etc/hosts on local machine and then log into the UI using the provided credentials."
