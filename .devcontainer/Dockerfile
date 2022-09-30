# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.187.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.8"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Set up base development environment. Patch SSL certs to work through VPN.
ARG ANTHEM_ROOT_PEM=/root.pem
ARG CERTIFI_PEM=/certifi.pem
ARG COMBINED_PEM=/combined.pem

COPY .devcontainer/resources/root.pem .

RUN curl -sSL https://raw.githubusercontent.com/certifi/python-certifi/master/certifi/cacert.pem --cacert ${ANTHEM_ROOT_PEM} > ${CERTIFI_PEM} \
    && cat ${CERTIFI_PEM} ${ANTHEM_ROOT_PEM} > ${COMBINED_PEM}

ENV SSL_CERT_FILE=${ANTHEM_ROOT_PEM}
ENV REQUESTS_CA_BUNDLE=${COMBINED_PEM}
ENV GIT_SSL_CAINFO=${COMBINED_PEM}

# Enable extension VSCODE extension to be installed in VPN
ENV NODE_EXTRA_CA_CERTS=${ANTHEM_ROOT_PEM}

RUN \
    # Set up certificate handling
    cat ${ANTHEM_ROOT_PEM} >> /etc/ssl/certs/ca-bundle.crt \
    && for f in $(find / -name cacert*.*); do cat ${ANTHEM_ROOT_PEM} >> $f; done \
    && git config --global http.sslcainfo ${ANTHEM_ROOT_PEM} \
    && cp /etc/ssl/certs/ca-bundle.crt /usr/local/share/ca-certificates/. \
    && update-ca-certificates \
    # Install packages
    && apt-get upgrade \
    && apt-get update \
    && apt-get install -y bash-completion curl \
    && pip install pre-commit

# Coding only for vscode user and not root
USER vscode

RUN curl -sSL https://install.python-poetry.org --cacert ${ANTHEM_ROOT_PEM} | python3 - \
    && bash -c "echo 'source <(poetry completions bash)' >> ~/.bashrc"
