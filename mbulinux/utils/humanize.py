"""
Human-readable formatting utilities.
"""

def humanize_size(size_bytes: int) -> str:
    """
    Convert size in bytes to human readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    
    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Format with appropriate precision
    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    elif size < 10:
        return f"{size:.2f} {units[unit_index]}"
    elif size < 100:
        return f"{size:.1f} {units[unit_index]}"
    else:
        return f"{int(size)} {units[unit_index]}"


def humanize_time(seconds: float) -> str:
    """
    Convert time in seconds to human readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Human readable string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def humanize_percent(value: float, total: float) -> str:
    """
    Format percentage.
    
    Args:
        value: Current value
        total: Total value
        
    Returns:
        Percentage string (e.g., "75.5%")
    """
    if total == 0:
        return "0%"
    
    percent = (value / total) * 100
    if percent.is_integer():
        return f"{int(percent)}%"
    else:
        return f"{percent:.1f}%"


def format_speed(bytes_per_second: float) -> str:
    """
    Format speed in bytes/second.
    
    Args:
        bytes_per_second: Speed in bytes per second
        
    Returns:
        Formatted speed string (e.g., "5.2 MB/s")
    """
    if bytes_per_second < 0:
        return "N/A"
    
    return f"{humanize_size(bytes_per_second)}/s"


def format_eta(remaining_bytes: int, speed_bytes_per_second: float) -> str:
    """
    Format estimated time remaining.
    
    Args:
        remaining_bytes: Bytes remaining
        speed_bytes_per_second: Current speed
        
    Returns:
        ETA string (e.g., "2m 30s")
    """
    if speed_bytes_per_second <= 0:
        return "Calculating..."
    
    remaining_seconds = remaining_bytes / speed_bytes_per_second
    return f"ETA: {humanize_time(remaining_seconds)}"