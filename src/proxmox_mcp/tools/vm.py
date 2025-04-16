"""
VM-related tools for Proxmox MCP.

This module provides tools for managing and interacting with Proxmox VMs:
- Listing all VMs across the cluster with their status
- Retrieving detailed VM information including:
  * Resource allocation (CPU, memory)
  * Runtime status
  * Node placement
- Executing commands within VMs via QEMU guest agent
- Handling VM console operations

The tools implement fallback mechanisms for scenarios where
detailed VM information might be temporarily unavailable.
"""
from typing import List
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from .definitions import GET_VMS_DESC, EXECUTE_VM_COMMAND_DESC
from .console.manager import VMConsoleManager

class VMTools(ProxmoxTool):
    """Tools for managing Proxmox VMs.
    
    Provides functionality for:
    - Retrieving cluster-wide VM information
    - Getting detailed VM status and configuration
    - Executing commands within VMs
    - Managing VM console operations
    
    Implements fallback mechanisms for scenarios where detailed
    VM information might be temporarily unavailable. Integrates
    with QEMU guest agent for VM command execution.
    """

    def __init__(self, proxmox_api):
        """Initialize VM tools.

        Args:
            proxmox_api: Initialized ProxmoxAPI instance
        """
        super().__init__(proxmox_api)
        self.console_manager = VMConsoleManager(proxmox_api)

    def get_vms(self) -> List[Content]:
        """List all virtual machines across the cluster with detailed status.

        Retrieves comprehensive information for each VM including:
        - Basic identification (ID, name)
        - Runtime status (running, stopped)
        - Resource allocation and usage:
          * CPU cores
          * Memory allocation and usage
        - Node placement
        
        Implements a fallback mechanism that returns basic information
        if detailed configuration retrieval fails for any VM.

        Returns:
            List of Content objects containing formatted VM information:
            {
                "vmid": "100",
                "name": "vm-name",
                "status": "running/stopped",
                "node": "node-name",
                "cpus": core_count,
                "memory": {
                    "used": bytes,
                    "total": bytes
                }
            }

        Raises:
            RuntimeError: If the cluster-wide VM query fails
        """
        try:
            result = []
            for node in self.proxmox.nodes.get():
                node_name = node["node"]
                vms = self.proxmox.nodes(node_name).qemu.get()
                for vm in vms:
                    vmid = vm["vmid"]
                    # Get VM config for CPU cores
                    try:
                        config = self.proxmox.nodes(node_name).qemu(vmid).config.get()
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": config.get("cores", "N/A"),
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
                    except Exception:
                        # Fallback if can't get config
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": "N/A",
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
            return self._format_response(result, "vms")
        except Exception as e:
            self._handle_error("get VMs", e)

    async def execute_command(self, node: str, vmid: str, command: str) -> List[Content]:
        """Execute a command in a VM via QEMU guest agent.

        Uses the QEMU guest agent to execute commands within a running VM.
        Requires:
        - VM must be running
        - QEMU guest agent must be installed and running in the VM
        - Command execution permissions must be enabled

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            command: Shell command to run (e.g., 'uname -a', 'systemctl status nginx')

        Returns:
            List of Content objects containing formatted command output:
            {
                "success": true/false,
                "output": "command output",
                "error": "error message if any"
            }

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If command execution fails due to permissions or other issues
        """
        try:
            result = await self.console_manager.execute_command(node, vmid, command)
            # Use the command output formatter from ProxmoxFormatters
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_command_output(
                success=result["success"],
                command=command,
                output=result["output"],
                error=result.get("error")
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"execute command on VM {vmid}", e)

    def change_vm_state(self, node: str, vmid: str, action: str) -> List[Content]:
        """Change the state of a VM (shutdown, start, reboot, pause, hibernate, reset, etc.).

        Args:
            node: Host node name (e.g., 'pve1')
            vmid: VM ID number (e.g., '100')
            action: Action to perform (e.g., 'start', 'stop', 'shutdown', 'reboot', 'reset', 'suspend', 'resume', 'pause', 'hibernate')

        Returns:
            List of Content objects indicating success or failure.

        Raises:
            ValueError: If the action is invalid or VM is not found
            RuntimeError: If the state change fails
        """
        try:
            valid_actions = [
                "start", "stop", "shutdown", "reboot", "reset", "suspend", "resume", "pause", "hibernate"
            ]
            if action not in valid_actions:
                raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

            # The Proxmox API uses .status.<action>.post() for most actions
            status_api = self.proxmox.nodes(node).qemu(vmid).status
            api_method = getattr(status_api, action, None)
            if not api_method:
                raise ValueError(f"Action '{action}' is not supported by the Proxmox API.")

            api_method.post()
            result = {
                "success": True,
                "action": action,
                "vmid": vmid,
                "node": node
            }
            return self._format_response(result)
        except Exception as e:
            self._handle_error(f"change VM state ({action}) for VM {vmid}", e)

    def create_vm(
        self,
        node: str,
        name: str,
        iso: str,
        cores: int = 2,
        memory: int = 2048,
        storage: str = "local-lvm"
    ) -> List[Content]:
        """Create (spin up) a new VM from a local ISO.

        Args:
            node: Host node name (e.g., 'pve1')
            name: Name for the new VM
            iso: ISO image filename from local storage (e.g., 'local:iso/ubuntu-22.04.iso')
            cores: Number of CPU cores (default: 2)
            memory: Memory in MB (default: 2048)
            storage: Storage pool to use (default: 'local-lvm')

        Returns:
            List of Content objects indicating success and new VMID.

        Raises:
            ValueError: If required parameters are missing or invalid
            RuntimeError: If VM creation fails
        """
        try:
            # Find the next available VMID
            vmid = self.proxmox.cluster.nextid.get()
            vmid = int(vmid)
            params = {
                "vmid": vmid,
                "name": name,
                "ide2": iso + ",media=cdrom",
                "ostype": "l26",
                "cores": cores,
                "memory": memory,
                "scsihw": "virtio-scsi-pci",
                "scsi0": f"{storage}:32",  # 32GB default disk
                "boot": "order=ide2;scsi0"
            }
            self.proxmox.nodes(node).qemu.post(**params)
            result = {
                "success": True,
                "vmid": vmid,
                "name": name,
                "node": node
            }
            return self._format_response(result)
        except Exception as e:
            self._handle_error("create VM", e)
