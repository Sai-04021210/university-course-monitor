# Node-RED Docker Development Environment

This project provides a portable, version-controlled Node-RED setup using Docker and local volumes for easy editing, collaboration, and backup.

## 🚀 Quick Start

1. **Clone this repo** on any system with Docker installed.
2. **Start Node-RED:**
   ```sh
   docker compose up -d
   ```
3. **Open Node-RED:** [http://localhost:1880](http://localhost:1880)
4. **Edit flows in the web UI** — changes are saved in `local-flows/`.
5. **Edit and version flows/settings** in VS Code or your editor of choice.

---

## 📁 Folder Structure

```
Node-Red/
├── .env                # Node-RED version and environment variables
├── .gitignore          # Ignores runtime and temp files
├── .vscode/settings.json # VS Code: hides internal files
├── docker-compose.yml  # Docker Compose setup
├── local-flows/        # All Node-RED user data (flows, credentials, etc.)
│   ├── flows.json
│   ├── flows_cred.json
│   └── ...
└── README.md
```

- **local-flows/**: All Node-RED runtime files (flows, credentials, etc.) are stored here. This folder is mapped to `/data` in the Docker container.
- **.vscode/settings.json**: Hides internal/noisy files from the VS Code explorer for a cleaner workspace.
- **.gitignore**: Ensures only important files are tracked in git.

---

## 🛠️ Changing Data Location

To use a different folder for your Node-RED data, update the `volumes` path in `docker-compose.yml`:

```yaml
volumes:
  - ./local-flows:/data  # Change './local-flows' to your desired path
```

---

## 📝 Best Practices

- **Edit flows in the Node-RED web UI** — changes are auto-saved to `local-flows/flows.json`.
- **Version control** your flows and settings for easy backup and collaboration.
- **Sensitive files** (like credentials) are encrypted in `flows_cred.json`.
- **Noisy/internal files** are hidden in VS Code and ignored by git.

---

## 🔄 Migrating or Collaborating

- Clone this repo on any machine, update the volume path if needed, and run `docker compose up -d`.
- All flows/settings are portable and ready to use!

---

## 📚 More Info
- [Node-RED Docs: Docker](https://nodered.org/docs/getting-started/docker)
- [Node-RED Docs: Projects](https://nodered.org/docs/user-guide/projects/)

---

Happy Node-RED hacking! 🎉
