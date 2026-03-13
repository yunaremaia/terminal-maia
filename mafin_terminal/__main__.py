"""MaFin Terminal - Run as module."""

import sys


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MaFin Terminal - Professional Financial Terminal")
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui', help='Launch mode (default: gui)')
    parser.add_argument('--fullscreen', action='store_true', help='Start in fullscreen mode (GUI only)')
    
    args = parser.parse_args()
    
    if args.mode == 'gui':
        from mafin_terminal.gui import launch_terminal
        launch_terminal()
    else:
        from mafin_terminal.cli import launch_cli
        launch_cli()


if __name__ == "__main__":
    main()
