#!/usr/bin/env python3
"""Entry point for context-overflow-mcp package."""

import asyncio
from .server import main

def cli_main():
    """CLI entry point."""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()