import logging, os


def get_logger():
    """Configures the logging module, and returns it

    Writes to a file log, also outputs it in the console
    """
    logger = logging.getLogger("python_app")
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler("../python_app.log")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def read_docker_secret(name: str) -> str:
    """
    Read a secret by name from as a docker configuration

    :param name: name of the secret
    :return: the secret as a string
    """
    with open(os.environ.get(name), "r") as file:
        return file.read()
