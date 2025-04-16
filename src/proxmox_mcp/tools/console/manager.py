"""
Module for managing VM console operations.

This module provides functionality for interacting with VM consoles:
- Executing commands within VMs via QEMU guest agent
- Handling command execution lifecycle
- Managing command output and status
- Error handling and logging

The module implements a robust command execution system with:
- VM state verification
- Asynchronous command execution
- Detailed status tracking
- Comprehensive error handling
"""

import logging
from typing import Dict, Any

class VMConsoleManager:
    """Manager class for VM console operations.
    
    Provides functionality for:
    - Executing commands in VM consoles
    - Managing command execution lifecycle
    - Handling command output and errors
    - Monitoring execution status
    
    Uses QEMU guest agent for reliable command execution with:
    - VM state verification before execution
    - Asynchronous command processing
    - Detailed output capture
    - Comprehensive error handling
    """

    def __init__(self, proxmox_api):
        """Initialize the VM console manager.

        Args:
            proxmox_api: Initialized ProxmoxAPI instance
        """
        self.proxmox = proxmox_api
        self.logger = logging.getLogger("proxmox-mcp.vm-console")

    async def execute_command(self, node: str, vmid: str, command: str) -> Dict[str, Any]:
        """Execute a command in a VM's console via QEMU guest agent.

        Implements a two-phase command execution process:
        1. Command Initiation:
           - Verifies VM exists and is running
           - Initiates command execution via guest agent
           - Captures command PID for tracking
        
        2. Result Collection:
           - Monitors command execution status
           - Captures command output and errors
           - Handles completion status
        
        Requirements:
        - VM must be running
        - QEMU guest agent must be installed and active
        - Command execution permissions must be enabled

        Args:
            node: Name of the node where VM is running (e.g., 'pve1')
            vmid: ID of the VM to execute command in (e.g., '100')
            command: Shell command to execute in the VM

        Returns:
            Dictionary containing command execution results:
            {
                "success": true/false,
                "output": "command output",
                "error": "error output if any",
                "exit_code": command_exit_code
            }

        Raises:
            ValueError: If:
                     - VM is not found
                     - VM is not running
                     - Guest agent is not available
            RuntimeError: If:
                       - Command execution fails
                       - Unable to get command status
                       - API communication errors occur
        """
        try:
            # Verify VM exists and is running
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            if vm_status["status"] != "running":
                self.logger.error(f"Failed to execute command on VM {vmid}: VM is not running")
                raise ValueError(f"VM {vmid} on node {node} is not running")

            # Get VM's console
            self.logger.info(f"Executing command on VM {vmid} (node: {node}): {command}")
            
            # Get the API endpoint
            # Use the guest agent exec endpoint
            endpoint = self.proxmox.nodes(node).qemu(vmid).agent
            self.logger.debug(f"Using API endpoint: {endpoint}")
            
            # Execute the command using two-step process
            try:
                # Start command execution
                self.logger.info("Starting command execution...")
                try:
                    self.logger.debug(f"Executing command via agent: {command}")
                    exec_result = endpoint("exec").post(command=command)
                    self.logger.debug(f"Raw exec response: {exec_result}")
                    self.logger.info(f"Command started with result: {exec_result}")
                except Exception as e:
                    self.logger.error(f"Failed to start command: {str(e)}")
                    raise RuntimeError(f"Failed to start command: {str(e)}")

                if 'pid' not in exec_result:
                    raise RuntimeError("No PID returned from command execution")

                pid = exec_result['pid']
                self.logger.info(f"Waiting for command completion (PID: {pid})...")

                # Add a small delay to allow command to complete
                import asyncio
                await asyncio.sleep(1)

                # Get command output using exec-status
                try:
                    self.logger.debug(f"Getting status for PID {pid}...")
                    console = endpoint("exec-status").get(pid=pid)
                    self.logger.debug(f"Raw exec-status response: {console}")
                    if not console:
                        raise RuntimeError("No response from exec-status")
                except Exception as e:
                    self.logger.error(f"Failed to get command status: {str(e)}")
                    raise RuntimeError(f"Failed to get command status: {str(e)}")
                self.logger.info(f"Command completed with status: {console}")
            except Exception as e:
                self.logger.error(f"API call failed: {str(e)}")
                raise RuntimeError(f"API call failed: {str(e)}")
            self.logger.debug(f"Raw API response type: {type(console)}")
            self.logger.debug(f"Raw API response: {console}")
            
            # Handle different response structures
            if isinstance(console, dict):
                # Handle exec-status response format
                output = console.get("out-data", "")
                error = console.get("err-data", "")
                exit_code = console.get("exitcode", 0)
                exited = console.get("exited", 0)
                
                if not exited:
                    self.logger.warning("Command may not have completed")
            else:
                # Some versions might return data differently
                self.logger.debug(f"Unexpected response type: {type(console)}")
                output = str(console)
                error = ""
                exit_code = 0
            
            self.logger.debug(f"Processed output: {output}")
            self.logger.debug(f"Processed error: {error}")
            self.logger.debug(f"Processed exit code: {exit_code}")
            
            self.logger.debug(f"Executed command '{command}' on VM {vmid} (node: {node})")

            return {
                "success": True,
                "output": output,
                "error": error,
                "exit_code": exit_code
            }

        except ValueError:
            # Re-raise ValueError for VM not running
            raise
        except Exception as e:
            self.logger.error(f"Failed to execute command on VM {vmid}: {str(e)}")
            if "not found" in str(e).lower():
                raise ValueError(f"VM {vmid} not found on node {node}")
            raise RuntimeError(f"Failed to execute command: {str(e)}")
