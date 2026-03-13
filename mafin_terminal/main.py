"""MaFin Terminal - Main entry point."""

import sys
import argparse


def main():
    """Main entry point for MaFin Terminal."""
    parser = argparse.ArgumentParser(description="MaFin Terminal")
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui', help='Launch mode')
    args, unknown = parser.parse_known_args()
    
    print(f"Starting MaFin Terminal ({args.mode} mode)...")
    
    if args.mode == 'cli':
        from mafin_terminal.cli import launch_cli
        launch_cli()
    else:
        from mafin_terminal.gui import launch_terminal
        launch_terminal()


if __name__ == "__main__":
    main()
