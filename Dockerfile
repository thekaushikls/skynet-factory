FROM node:20-bookworm-slim

ARG UPDATE_APT=true
ARG UPDATE_NPM=true
ARG DISPLAY_BANNER=false
ARG INSTALL_GEMINI=false
ARG INSTALL_OPENCODE=false

# Install cURL
RUN if [ "$UPDATE_APT" = "true" ]; then apt update && apt upgrade -y; fi

# Update npm if requested
RUN if [ "$UPDATE_NPM" = "true" ]; then npm install -g npm@latest; fi

# Install AI CLI tools if requested
RUN if [ "$INSTALL_GEMINI" = "true" ]; then npm install -g @google/gemini-cli; fi
RUN if [ "$INSTALL_OPENCODE" = "true" ]; then npm install -g opencode-ai; fi
# Setup terminal banner if requested
COPY scripts/add_banner.sh /tmp/add_banner.sh
RUN if [ "$DISPLAY_BANNER" = "true" ]; then \
    chmod +x /tmp/add_banner.sh && \
    /tmp/add_banner.sh && \
    rm /tmp/add_banner.sh; \
    fi

WORKDIR /workspace
