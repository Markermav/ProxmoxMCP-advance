"""
Theme configuration for Proxmox MCP output styling.
"""

class ProxmoxTheme:
    """Theme configuration for Proxmox MCP output."""
    
    # Feature flags
    USE_EMOJI = True
    USE_COLORS = True
    
    # Status indicators with emojis
    STATUS = {
        'online': '🟢',
        'offline': '🔴',
        'running': '▶️',
        'stopped': '⏹️',
        'unknown': '❓',
        'pending': '⏳',
        'error': '❌',
        'warning': '⚠️',
    }
    
    # Resource type indicators
    RESOURCES = {
        'node': '🖥️',
        'vm': '🗃️',
        'container': '📦',
        'storage': '💾',
        'cpu': '⚡',
        'memory': '🧠',
        'network': '🌐',
        'disk': '💿',
        'backup': '📼',
        'snapshot': '📸',
        'template': '📋',
        'pool': '🏊',
    }
    
    # Action and operation indicators
    ACTIONS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'command': '🔧',
        'start': '▶️',
        'stop': '⏹️',
        'restart': '🔄',
        'delete': '🗑️',
        'edit': '✏️',
        'create': '➕',
        'migrate': '➡️',
        'clone': '📑',
        'lock': '🔒',
        'unlock': '🔓',
    }
    
    # Section and grouping indicators
    SECTIONS = {
        'header': '📌',
        'details': '📝',
        'statistics': '📊',
        'configuration': '⚙️',
        'logs': '📜',
        'tasks': '📋',
        'users': '👥',
        'permissions': '🔑',
    }
    
    # Measurement and metric indicators
    METRICS = {
        'percentage': '%',
        'temperature': '🌡️',
        'uptime': '⏳',
        'bandwidth': '📶',
        'latency': '⚡',
    }
    
    @classmethod
    def get_status_emoji(cls, status: str) -> str:
        """Get emoji for a status value with fallback."""
        status = status.lower()
        return cls.STATUS.get(status, cls.STATUS['unknown'])
    
    @classmethod
    def get_resource_emoji(cls, resource: str) -> str:
        """Get emoji for a resource type with fallback."""
        resource = resource.lower()
        return cls.RESOURCES.get(resource, '📦')
    
    @classmethod
    def get_action_emoji(cls, action: str) -> str:
        """Get emoji for an action with fallback."""
        action = action.lower()
        return cls.ACTIONS.get(action, cls.ACTIONS['info'])
    
    @classmethod
    def get_section_emoji(cls, section: str) -> str:
        """Get emoji for a section type with fallback."""
        section = section.lower()
        return cls.SECTIONS.get(section, cls.SECTIONS['details'])
