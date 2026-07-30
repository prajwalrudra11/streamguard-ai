"""
StreamGuard AI - Structured Logging Configuration
"""
import sys
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging with loguru."""
    
    # Remove default handler
    logger.remove()
    
    # Ensure stdout supports UTF-8 (particularly on Windows)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError, OSError):
        pass
    
    def console_sink(message):
        try:
            sys.stdout.write(message)
            sys.stdout.flush()
        except UnicodeEncodeError:
            encoding = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
            safe_message = message.encode(encoding, errors="replace").decode(encoding)
            sys.stdout.write(safe_message)
            sys.stdout.flush()

    # Console handler with color formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        console_sink,
        format=log_format,
        level="DEBUG" if debug else "INFO",
        colorize=True,
    )
    
    # File handler for persistent logs
    logger.add(
        "logs/streamguard_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("🛡️ StreamGuard AI logging initialized")


def get_logger(name: str):
    """Get a named logger instance."""
    return logger.bind(module=name)
