FROM node:20-bookworm-slim

ARG UPDATE_APT=true
ARG UPDATE_NPM=true
ARG INSTALL_GEMINI=false
ARG INSTALL_OPENCODE=false

# Install cURL
RUN if [ "$UPDATE_APT" = "true" ]; then apt update && apt upgrade -y; fi

# Update npm if requested
RUN if [ "$UPDATE_NPM" = "true" ]; then npm install -g npm@latest; fi

# Install AI CLI tools if requested
RUN if [ "$INSTALL_GEMINI" = "true" ]; then npm install -g @google/gemini-cli; fi
RUN if [ "$INSTALL_OPENCODE" = "true" ]; then npm install -g opencode-ai; fi

WORKDIR /workspace
