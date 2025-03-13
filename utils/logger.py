# utils/logger.py
import logging
import sys

def setup_logger(log_file=None, log_level=logging.INFO):
    """
    Konfigurasi logging.

    Args:
        log_file (str, optional): Nama file untuk logging. Jika None, log ke stdout.
        log_level (int, optional): Level logging (e.g., logging.DEBUG, logging.INFO).
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Handler untuk console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Handler untuk file (jika disediakan)
    file_handler = None
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

    # Buat logger dan tambahkan handler
    logger = logging.getLogger()  # Root logger
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)

# Contoh Penggunaan
if __name__ == '__main__':
    setup_logger(log_file="my_app.log", log_level=logging.DEBUG)  # Log ke file dan console
    # setup_logger() # Hanya Log ke Console

    log = logging.getLogger(__name__)  # Dapatkan logger
    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message.")