import logging

def helper_setup_logging(log_level=logging.INFO):
    """Configure logging for the entire application."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Log to console
            # Add FileHandler or other handlers if needed
        ]
    )
    return logging.getLogger(__name__)
