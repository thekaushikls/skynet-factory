![Skynet Factory](assets/banner.png)

# Skynet Factory
- Lightweight development environment.
- Containerized workspace for AI CLI tools (Gemini, OpenCode)

## Bind Mounts

The container uses bind mounts to sync your local workspace with the container filesystem:

- **Host Path**: Defined by `WORKSPACE_SOURCE` in `.env` (e.g., `X:/skynet/workspace`)
- **Container Path**: Defined by `WORKSPACE_TARGET` in `.env` (default: `/workspace`)

All files in your source directory are accessible inside the container at the target path, allowing seamless development with persistent data.

## ENV sample

Create a `.env` file from `.env.sample`:

```env
WORKSPACE_SOURCE=X:/skynet/workspace
WORKSPACE_TARGET=/workspace

UPDATE_NPM=true
INSTALL_GEMINI=false
INSTALL_OPENCODE=true
```

- `WORKSPACE_SOURCE`: Local directory to mount
- `WORKSPACE_TARGET`: Mount point inside container
- `UPDATE_NPM`: Update npm to latest version on build
- `INSTALL_GEMINI`: Install Google Gemini CLI tool
- `INSTALL_OPENCODE`: Install OpenCode AI CLI tool

## Usage

Start the container using Docker Compose:

```bash
docker-compose up -d
```

Access the running container using the `skynet.bat` script:

```bash
skynet.bat
```

The script will:
- Check Docker daemon status
- Verify Skynet container is running
- Display npm version
- Launch an interactive bash session

Stop the container:

```bash
docker-compose down
```
