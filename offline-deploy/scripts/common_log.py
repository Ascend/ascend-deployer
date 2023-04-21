import logging
import logging.handlers
import os
import stat

PERMS_600 = stat.S_IRUSR | stat.S_IWUSR
class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    rewrite RotatingFileHandler, chmod 600 downloader.log and chmod 400 downloader.log.*
    """

    def doRollover(self):
        largest_backfile = "{}.{}".format(self.baseFilename, 5)
        if os.path.exists(largest_backfile):
            os.chmod(largest_backfile, PERMS_600)
        os.chmod(self.baseFilename, stat.S_IRUSR)
        logging.handlers.RotatingFileHandler.doRollover(self)
        os.chmod(self.baseFilename, PERMS_600)


class BasicLogConfig(object):
    """
    basic logger configuration
    """
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    working_env = os.environ.copy()
    LOG_FILE = "{}/.log/mindx-dl-install.log".format(working_env.get("HOME", "/root"))
    LOG_PATH = "{}/.log".format(working_env.get("HOME", "/root"))
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    if not os.path.exists(LOG_FILE):
        os.close(os.open(LOG_FILE, os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR))
    else:
        os.chmod(LOG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_FORMAT_STRING_ANSIBLE = \
        "%(asctime)s ansible [%(levelname)s] " \
        "[%(filename)s:%(lineno)d] %(message)s"
    LOG_FORMAT_STRING_DEPLOYER = \
        "%(asctime)s ascend_deployer [%(levelname)s] " \
        "[%(filename)s:%(lineno)d] %(message)s"
    LOG_LEVEL = logging.INFO

    ROTATING_CONF = dict(
        mode='a',
        maxBytes=20 * 1024 * 1024,
        backupCount=5,
        encoding="UTF-8")


def Get_logger_ansible(name):
    """
    get_logger
    """
    log_conf = BasicLogConfig()
    logger = logging.getLogger(name)
    rotating_handler = RotatingFileHandler(
        filename=log_conf.LOG_FILE, **log_conf.ROTATING_CONF)
    log_formatter = logging.Formatter(
        log_conf.LOG_FORMAT_STRING_ANSIBLE, log_conf.LOG_DATE_FORMAT)
    rotating_handler.setFormatter(log_formatter)
    logger.addHandler(rotating_handler)
    logger.setLevel(log_conf.LOG_LEVEL)
    return logger


def Get_logger_deploy(name):
    """
    get_logger
    """
    log_conf = BasicLogConfig()
    logger = logging.getLogger(name)
    rotating_handler = RotatingFileHandler(
        filename=log_conf.LOG_FILE, **log_conf.ROTATING_CONF)
    log_formatter = logging.Formatter(
        log_conf.LOG_FORMAT_STRING_DEPLOYER, log_conf.LOG_DATE_FORMAT)
    rotating_handler.setFormatter(log_formatter)
    ch = logging.StreamHandler()
    ch.setLevel('INFO')
    ch.setFormatter(log_formatter)
    logger.addHandler(rotating_handler)
    logger.addHandler(ch)
    logger.setLevel(log_conf.LOG_LEVEL)
    return logger