"""
Tests for VM console operations.
"""

import pytest
from unittest.mock import Mock, patch

from proxmox_mcp.tools.vm_console import VMConsoleManager

@pytest.fixture
def mock_proxmox():
    """Fixture to create a mock ProxmoxAPI instance."""
    mock = Mock()
    # Setup chained mock calls
    mock.nodes.return_value.qemu.return_value.status.current.get.return_value = {
        "status": "running"
    }
    mock.nodes.return_value.qemu.return_value.agent.exec.post.return_value = {
        "out": "command output",
        "err": "",
        "exitcode": 0
    }
    return mock

@pytest.fixture
def vm_console(mock_proxmox):
    """Fixture to create a VMConsoleManager instance."""
    return VMConsoleManager(mock_proxmox)

@pytest.mark.asyncio
async def test_execute_command_success(vm_console, mock_proxmox):
    """Test successful command execution."""
    result = await vm_console.execute_command("node1", "100", "ls -l")

    assert result["success"] is True
    assert result["output"] == "command output"
    assert result["error"] == ""
    assert result["exit_code"] == 0

    # Verify correct API calls
    mock_proxmox.nodes.return_value.qemu.assert_called_with("100")
    mock_proxmox.nodes.return_value.qemu.return_value.agent.exec.post.assert_called_with(
        command="ls -l"
    )

@pytest.mark.asyncio
async def test_execute_command_vm_not_running(vm_console, mock_proxmox):
    """Test command execution on stopped VM."""
    mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
        "status": "stopped"
    }

    with pytest.raises(ValueError, match="not running"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_vm_not_found(vm_console, mock_proxmox):
    """Test command execution on non-existent VM."""
    mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.side_effect = \
        Exception("VM not found")

    with pytest.raises(ValueError, match="not found"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_failure(vm_console, mock_proxmox):
    """Test command execution failure."""
    mock_proxmox.nodes.return_value.qemu.return_value.agent.exec.post.side_effect = \
        Exception("Command failed")

    with pytest.raises(RuntimeError, match="Failed to execute command"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_with_error_output(vm_console, mock_proxmox):
    """Test command execution with error output."""
    mock_proxmox.nodes.return_value.qemu.return_value.agent.exec.post.return_value = {
        "out": "",
        "err": "command error",
        "exitcode": 1
    }

    result = await vm_console.execute_command("node1", "100", "invalid-command")

    assert result["success"] is True  # Success refers to API call, not command
    assert result["output"] == ""
    assert result["error"] == "command error"
    assert result["exit_code"] == 1
