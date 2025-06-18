# University Course Monitor

A Node-RED based application that monitors German universities for new courses and sends notifications via email when new courses are added to MyGermanUniversity website.

## Features

- **University Course Monitoring**: Automatically scrapes MyGermanUniversity for new course listings
- **Email Notifications**: Sends alerts when new courses are detected
- **Dashboard Interface**: View monitored universities and recent notifications
- **Configurable**: Easy setup for different universities and notification preferences

## Quick Start

1. Clone this repository:
   ```sh
   git clone <repository-url>
   cd university-course-monitor
   ```
2. Start the application:
   ```sh
   docker compose up -d
   ```
3. Open Node-RED Dashboard: [http://localhost:1880](http://localhost:1880)
4. Configure your monitoring settings and email preferences

---

## Folder Structure

### Node-RED Classic Setup

- This setup uses the classic Node-RED workflow with a single flow file (`flows.json`) and configuration in the `workspace/` directory.
- All flows, credentials, and settings are stored in `workspace/` for easy editing and version control.
- No Projects mode is enabled; all development is done in a single workspace.
- Example structure:

```
workspace/
├── flows.json
├── flows_cred.json
├── settings.js
├── package.json
```

```
Node-Red/
├── .env                   # Node-RED version and environment variables
├── .gitignore             # Ignores runtime and temporary files
├── .vscode/settings.json  # VS Code: hides internal files
├── docker-compose.yml     # Docker Compose setup
├── workspace/           # All Node-RED user data (flows, credentials, etc.)
│   ├── flows.json
│   ├── flows_cred.json
│   └── ...
└── README.md
```

- workspace/: All Node-RED runtime files (flows, credentials, etc.) are stored here. This folder is mapped to `/data` in the Docker container.
- .vscode/settings.json: Hides internal or noisy files from the VS Code explorer for a cleaner workspace.
- .gitignore: Ensures only important files are tracked in git.

---

## Changing Data Location

To use a different folder for your Node-RED data, update the `volumes` path in `docker-compose.yml`:

```yaml
volumes:
  - ./workspace:/data  # Change './workspace' to your desired path
```

---

## Best Practices

- Edit flows in the Node-RED web UI; changes are auto-saved to `workspace/flows.json`.
- Version control your flows and settings for easy backup and collaboration.
- Sensitive files (such as credentials) are encrypted in `flows_cred.json`.
- Internal files are hidden in VS Code and ignored by git.

---

## Migrating or Collaborating

- Clone this repository on any machine, update the volume path if needed, and run `docker compose up -d`.
- All flows and settings are portable and ready to use.

---

## References

- [Node-RED Documentation: Docker](https://nodered.org/docs/getting-started/docker)
- [Node-RED Documentation: Projects](https://nodered.org/docs/user-guide/projects/)

---
