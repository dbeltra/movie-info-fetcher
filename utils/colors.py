"""Terminal color utilities and output formatting."""

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_colored(text: str, color: str = Colors.END) -> None:
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}")


def print_progress_bar(current: int, total: int, width: int = 50) -> None:
    """Print a progress bar"""
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    print(f"\r{Colors.BLUE}Progress: [{bar}] {current}/{total} ({percent:.1%}){Colors.END}", end='', flush=True)
