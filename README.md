# 🦸 Proxmox MCP Server Manager (Advanced Edition)

<!-- **🎬 Demo Video:**  
See `ProxmoxMCP/Proxmox-adv-demo.webm` for a full demonstration of advanced features. -->

---

## ✨ What's New in This Release

**Advanced Features Recently Added:**

- 🟢 **Start/Stop/Manage VMs:** Instantly start, stop, or reboot any VM in your cluster.
- 🖥️ **In-VM Command Execution:** Run system updates, install packages (e.g., nginx), and patch VMs directly from the MCP interface.
- ⚡ **Automated VM Provisioning:** Spin up new VMs from any ISO with default or custom resources in a single command.
- 📊 **Cluster Resource Overview:** List all nodes, VMs, and storage pools with real-time status and resource usage.
- 🔒 **Secure Configuration:** All sensitive credentials are managed via config files and environment variables, never hardcoded.
- 🧑‍💻 **Rich CLI/VSCode Integration:** Seamless operation with Cline and VSCode for automated workflows.
- 🎬 **Demo Video:** See `ProxmoxMCP/Proxmox-adv-demo.webm` for a walkthrough of these features.

---

## 🖥️ Setting Up Proxmox on a Virtual Machine Manager

**📝 Step-by-step guide to install Proxmox using the official ISO:**

1. 📥 **Download the Proxmox ISO:**
   - Visit the [Proxmox Downloads page](https://www.proxmox.com/en/downloads) and download the latest Proxmox VE ISO (e.g., `proxmox-ve_8.x.iso`).

2. 🆕 **Create a New Virtual Machine:**
   - Open your Virtual Machine Manager (e.g., virt-manager, VMware, VirtualBox).
   - Create a new VM and select the downloaded Proxmox ISO as the installation media.
   - Assign at least 2 CPU cores, 4GB RAM, and 32GB disk (recommended for testing).
   - Configure networking (bridged or NAT as needed).

3. 💿 **Install Proxmox:**
   - Boot the VM from the ISO and follow the on-screen instructions to install Proxmox VE.
   - Set a secure password and note the IP address assigned to the VM.

4. ⚙️ **Initial Configuration:**
   - Access the Proxmox web UI at `https://<proxmox-vm-ip>:8006` from your browser.
   - Complete the setup wizard, configure storage, and create an admin user if needed.

5. 🔑 **API Token Setup:**
   - In the Proxmox web UI, go to Datacenter → Permissions → API Tokens.
   - Create a new API token for your user (e.g., `Markermav@pam`). #Example user here!
   - Save the token name and value securely.

6. 🛰️ **Enable QEMU Guest Agent (for VM command execution):**
   - For each VM you want to manage, install the QEMU Guest Agent:
     ```
     apt-get update
     apt-get install -y qemu-guest-agent
     systemctl enable --now qemu-guest-agent
     ```
   - Ensure the agent is enabled in the VM's options settings in Proxmox.
   - Right click on VM → Options → enable QEMU Guest Agent. (**without this agent will not start)

---

## 🗂️ Configuration Example

**proxmox-config/config.json** (with sensitive info replaced):

```json
{
    "proxmox": {
        "host": "proxmox.example.local",
        "port": 8006,
        "verify_ssl": false,
        "service": "PVE"
    },
    "auth": {
        "user": "Markermav@pam", #Example user here!
        "token_name": "mcp-token",
        "token_value": "your-token-value"
    },
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "proxmox_mcp.log"
    }
}
```

---

## 📦 Installation

### 🛠️ Prerequisites

- 🐍 Python 3.10+
- 🧬 Git
- 📦 UV package manager (`pip install uv`)
- 🔗 Access to a Proxmox server with API token credentials

### ⚡ Quick Install

```bash
git clone https://github.com/Markermav/ProxmoxMCP.git
cd ProxmoxMCP
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
mkdir -p proxmox-config
cp config/config.example.json proxmox-config/config.json
# Edit proxmox-config/config.json with your Proxmox details
```

---

## 🚀 Running the Server

**Development Mode:**

```bash
source .venv/bin/activate
python -m proxmox_mcp.server
```

**Cline Desktop Integration:**

Add this to your MCP settings (replace paths and sensitive info):

```json
{
  "mcpServers": {
    "github.com/Markermav/ProxmoxMCP": {
      "command": "/home/Markermav/ProxmoxMCP/.venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/home/Markermav/ProxmoxMCP",
      "env": {
        "PYTHONPATH": "/home/Markermav/ProxmoxMCP/src",
        "PROXMOX_MCP_CONFIG": "/home/Markermav/ProxmoxMCP/proxmox-config/config.json",
        "PROXMOX_HOST": "proxmox.example.local",
        "PROXMOX_USER": "Markermav@pam", #Example user here!
        "PROXMOX_TOKEN_NAME": "mcp-token",
        "PROXMOX_TOKEN_VALUE": "your-token-value",
        "PROXMOX_PORT": "8006",
        "PROXMOX_VERIFY_SSL": "false",
        "PROXMOX_SERVICE": "PVE",
        "LOG_LEVEL": "DEBUG"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 🧰 Available Tools

- 🖥️ **List Nodes:** View all nodes in the cluster with status and resource usage.
- 📡 **Node Status:** Get detailed info for any node.
- 🗃️ **List VMs:** See all VMs, their status, and resources.
- 🔄 **VM State Management:** Start, stop, reboot, suspend, or reset VMs.
- 🛰️ **In-VM Command Execution:** Run any shell command in a VM (requires QEMU Guest Agent).
- 💾 **Storage Overview:** List all storage pools and usage.
- 🏥 **Cluster Health:** Get overall cluster status and health.

---

## 🏗️ Project Structure

```
proxmox-mcp/
├── src/
│   └── proxmox_mcp/
│       ├── server.py
│       ├── config/
│       ├── core/
│       ├── formatting/
│       ├── tools/
│       │   └── console/
│       └── utils/
├── tests/
├── proxmox-config/
│   └── config.example.json
├── pyproject.toml
└── LICENSE
```

---

## 📄 License

MIT License
