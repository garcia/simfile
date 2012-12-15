__all__ = ['getch', 'enum']

def getch():
    """Provides cross-platform getch() functionality."""
    try:
        import msvcrt
        return msvcrt.getch()
    except ImportError:
        import sys
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def enum(*sequential, **named):
    """Creates an enum out of both sequential and named elements."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)