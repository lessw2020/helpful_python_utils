#!/usr/bin/env python3
"""
Script to inspect and display current logging configuration.
Shows all loggers, handlers, formatters, and their settings.
"""

import logging
import sys
from typing import Any, Dict, List


def get_handler_info(handler: logging.Handler) -> Dict[str, Any]:
    """Extract detailed information about a logging handler."""
    info = {
        "type": type(handler).__name__,
        "level": logging.getLevelName(handler.level),
        "level_num": handler.level,
    }

    # Get formatter info
    if handler.formatter:
        fmt = handler.formatter
        info["formatter"] = {
            "format": getattr(fmt, "_fmt", "N/A"),
            "datefmt": getattr(fmt, "datefmt", "N/A"),
            "style": getattr(fmt, "_style", "N/A"),
        }
    else:
        info["formatter"] = None

    # Handler-specific attributes
    if isinstance(handler, logging.FileHandler):
        info["filename"] = getattr(handler, "baseFilename", "N/A")
        info["mode"] = getattr(handler, "mode", "N/A")
        info["encoding"] = getattr(handler, "encoding", "N/A")

    elif isinstance(handler, logging.StreamHandler):
        stream = getattr(handler, "stream", None)
        if stream:
            info["stream"] = stream.name if hasattr(stream, "name") else str(stream)
        else:
            info["stream"] = "N/A"

    # Use direct class checks instead of accessing through logging._handlers
    elif hasattr(logging, "RotatingFileHandler") and isinstance(
        handler, logging.RotatingFileHandler
    ):
        info["filename"] = getattr(handler, "baseFilename", "N/A")
        info["maxBytes"] = getattr(handler, "maxBytes", "N/A")
        info["backupCount"] = getattr(handler, "backupCount", "N/A")

    elif hasattr(logging, "TimedRotatingFileHandler") and isinstance(
        handler, logging.TimedRotatingFileHandler
    ):
        info["filename"] = getattr(handler, "baseFilename", "N/A")
        info["when"] = getattr(handler, "when", "N/A")
        info["interval"] = getattr(handler, "interval", "N/A")
        info["backupCount"] = getattr(handler, "backupCount", "N/A")

    # Filters
    if hasattr(handler, "filters") and handler.filters:
        info["filters"] = [type(f).__name__ for f in handler.filters]
    else:
        info["filters"] = []

    return info


def get_logger_info(logger: logging.Logger) -> Dict[str, Any]:
    """Extract detailed information about a logger."""
    return {
        "name": logger.name,
        "level": logging.getLevelName(logger.level),
        "level_num": logger.level,
        "effective_level": logging.getLevelName(logger.getEffectiveLevel()),
        "effective_level_num": logger.getEffectiveLevel(),
        "propagate": logger.propagate,
        "disabled": logger.disabled,
        "handlers": [get_handler_info(h) for h in logger.handlers],
        "filters": [type(f).__name__ for f in logger.filters] if logger.filters else [],
        "parent": logger.parent.name if logger.parent else None,
    }


def print_handler_details(handler_info: Dict[str, Any], indent: str = "    ") -> None:
    """Print detailed handler information."""
    print(f"{indent}Type: {handler_info['type']}")
    print(f"{indent}Level: {handler_info['level']} ({handler_info['level_num']})")

    # Handler-specific info
    if "filename" in handler_info:
        print(f"{indent}File: {handler_info['filename']}")
    if "stream" in handler_info:
        print(f"{indent}Stream: {handler_info['stream']}")
    if "mode" in handler_info:
        print(f"{indent}Mode: {handler_info['mode']}")
    if "encoding" in handler_info:
        print(f"{indent}Encoding: {handler_info['encoding']}")
    if "maxBytes" in handler_info:
        print(f"{indent}Max Bytes: {handler_info['maxBytes']}")
    if "backupCount" in handler_info:
        print(f"{indent}Backup Count: {handler_info['backupCount']}")
    if "when" in handler_info:
        print(f"{indent}When: {handler_info['when']}")
    if "interval" in handler_info:
        print(f"{indent}Interval: {handler_info['interval']}")

    # Formatter info
    if handler_info["formatter"]:
        fmt = handler_info["formatter"]
        print(f"{indent}Formatter:")
        print(f"{indent}  Format: {fmt['format']}")
        print(f"{indent}  Date Format: {fmt['datefmt']}")
        print(f"{indent}  Style: {fmt['style']}")
    else:
        print(f"{indent}Formatter: None")

    # Filters
    if handler_info["filters"]:
        print(f"{indent}Filters: {', '.join(handler_info['filters'])}")
    else:
        print(f"{indent}Filters: None")


def show_root_logger() -> None:
    """Display root logger information with handler source."""
    print("🌟 ROOT LOGGER")
    print("=" * 50)

    root_logger = logging.getLogger()
    root_info = get_logger_info(root_logger)

    print(f"Level: {root_info['level']} ({root_info['level_num']})")
    print(
        f"Effective Level: {root_info['effective_level']} ({root_info['effective_level_num']})"
    )
    print(f"Disabled: {root_info['disabled']}")
    print(f"Handlers: {len(root_info['handlers'])}")

    if root_info["filters"]:
        print(f"Filters: {', '.join(root_info['filters'])}")
    else:
        print("Filters: None")

    print()

    # Show handlers with source information
    if root_info["handlers"]:
        print("📋 ROOT LOGGER HANDLERS")
        print("-" * 30)
        for i, handler_info in enumerate(root_info["handlers"], 1):
            print(f"Handler {i}:")
            print_handler_details(handler_info)

            # Try to find where this handler was added
            handler = root_logger.handlers[i - 1]
            handler_id = id(handler)
            print(f"    Handler ID: {handler_id}")

            # Get handler creation stack if available
            if hasattr(handler, "__module__"):
                print(f"    Module: {handler.__module__}")

            print()
    else:
        print("📋 ROOT LOGGER HANDLERS: None")
        print()


def show_all_loggers() -> None:
    """Display all configured loggers."""
    print("📚 ALL LOGGERS")
    print("=" * 50)

    # Get all loggers
    logger_dict = logging.Logger.manager.loggerDict

    if not logger_dict:
        print("No named loggers configured.")
        return

    # Sort loggers by name for better readability
    sorted_loggers = sorted(logger_dict.items())

    print(f"Total loggers: {len(sorted_loggers)}")
    print()

    for name, logger_obj in sorted_loggers:
        # Skip PlaceHolder objects
        if isinstance(logger_obj, logging.PlaceHolder):
            print(f"📍 {name} (PlaceHolder)")
            continue

        if isinstance(logger_obj, logging.Logger):
            logger_info = get_logger_info(logger_obj)

            print(f"📖 {name}")
            print(f"  Level: {logger_info['level']} ({logger_info['level_num']})")
            print(
                f"  Effective Level: {logger_info['effective_level']} ({logger_info['effective_level_num']})"
            )
            print(f"  Propagate: {logger_info['propagate']}")
            print(f"  Disabled: {logger_info['disabled']}")
            print(f"  Parent: {logger_info['parent'] or 'root'}")
            print(f"  Handlers: {len(logger_info['handlers'])}")

            if logger_info["filters"]:
                print(f"  Filters: {', '.join(logger_info['filters'])}")

            # Show handlers if any
            if logger_info["handlers"]:
                for i, handler_info in enumerate(logger_info["handlers"], 1):
                    print(
                        f"    Handler {i}: {handler_info['type']} (Level: {handler_info['level']})"
                    )

            print()


def show_logger_hierarchy() -> None:
    """Display logger hierarchy."""
    print("🌳 LOGGER HIERARCHY")
    print("=" * 50)

    def print_logger_tree(logger: logging.Logger, indent: int = 0) -> None:
        """Recursively print logger hierarchy."""
        prefix = "  " * indent
        level_info = f"{logger.getEffectiveLevel()}"
        handlers_info = (
            f"({len(logger.handlers)} handlers)" if logger.handlers else "(no handlers)"
        )

        print(
            f"{prefix}├─ {logger.name or 'root'} [Level: {level_info}] {handlers_info}"
        )

        # Find child loggers
        logger_dict = logging.Logger.manager.loggerDict
        children = []

        for name, child_logger in logger_dict.items():
            if isinstance(child_logger, logging.Logger):
                if child_logger.parent == logger:
                    children.append(child_logger)

        # Sort children by name
        children.sort(key=lambda x: x.name)

        for child in children:
            print_logger_tree(child, indent + 1)

    root_logger = logging.getLogger()
    print_logger_tree(root_logger)
    print()


def show_handler_summary() -> None:
    """Show summary of all handlers across all loggers."""
    print("🔧 HANDLER SUMMARY")
    print("=" * 50)

    all_handlers = []
    handler_types = {}

    # Collect handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        all_handlers.append(("root", handler))

    # Collect handlers from all other loggers
    logger_dict = logging.Logger.manager.loggerDict
    for name, logger_obj in logger_dict.items():
        if isinstance(logger_obj, logging.Logger):
            for handler in logger_obj.handlers:
                all_handlers.append((name, handler))

    # Count handler types
    for logger_name, handler in all_handlers:
        handler_type = type(handler).__name__
        if handler_type not in handler_types:
            handler_types[handler_type] = []
        handler_types[handler_type].append((logger_name, handler))

    print(f"Total handlers: {len(all_handlers)}")
    print(f"Handler types: {len(handler_types)}")
    print()

    for handler_type, handlers in sorted(handler_types.items()):
        print(f"📌 {handler_type} ({len(handlers)} instances)")
        for logger_name, handler in handlers:
            level = logging.getLevelName(handler.level)
            print(f"  └─ Logger: {logger_name}, Level: {level}")
        print()


def show_logging_config() -> None:
    """Show current logging module configuration."""
    print("⚙️  LOGGING CONFIGURATION")
    print("=" * 50)

    print(f"Python version: {sys.version}")
    print(f"Logging module: {logging.__file__}")
    print()

    # Show important logging attributes
    print("Global Settings:")
    print(f"  Root logger level: {logging.getLevelName(logging.getLogger().level)}")
    print(f"  Last resort handler: {logging.lastResort}")
    print(
        f"  Capture warnings: {logging.captureWarnings.__defaults__}"
    )  # This might not work in all versions
    print()

    # Show level names
    print("Level Names:")
    levels = [
        (logging.CRITICAL, "CRITICAL"),
        (logging.ERROR, "ERROR"),
        (logging.WARNING, "WARNING"),
        (logging.INFO, "INFO"),
        (logging.DEBUG, "DEBUG"),
        (logging.NOTSET, "NOTSET"),
    ]

    for level_num, level_name in levels:
        print(f"  {level_name}: {level_num}")
    print()


def main() -> None:
    """Main function to run all inspections."""
    print("🔍 PYTHON LOGGING INSPECTOR")
    print("=" * 60)
    print()

    show_logging_config()
    show_root_logger()
    # Comment out other sections to focus on root logger
    # show_all_loggers()
    # show_logger_hierarchy()
    # show_handler_summary()

    print("✅ Inspection complete!")


def main_old() -> None:
    """Main function to run all inspections."""
    print("🔍 PYTHON LOGGING INSPECTOR")
    print("=" * 60)
    print()

    show_logging_config()
    show_root_logger()
    show_all_loggers()
    show_logger_hierarchy()
    show_handler_summary()

    print("✅ Inspection complete!")


if __name__ == "__main__":
    main()
