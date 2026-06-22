FROM node:24-bookworm-slim

ARG DISPLAY_BANNER=false
ARG INSTALL_CLAUDE=false
ARG INSTALL_CODEX=false
ARG INSTALL_GEMINI=false
ARG INSTALL_OPENCODE=false

# Update system packages and install essentials
RUN apt update && apt upgrade -y && apt install -y nano git && apt install -y curl

# Update npm
RUN npm install -g npm@latest

# Install AI CLI tools if requested
RUN if [ "$INSTALL_CLAUDE" = "true" ]; then npm install -g @anthropic-ai/claude-code; fi
RUN if [ "$INSTALL_CODEX" = "true" ]; then npm install -g @openai/codex; fi
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
