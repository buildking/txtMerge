import logging
import os
from config import ConfigUtil

def setLogging(_logName="log"):
    log_level = ConfigUtil.config.get("log", 'log_level', fallback='INFO')
    log_dir = ConfigUtil.config.get("log", 'log_dir', fallback='log')
    log_file = ConfigUtil.config.get("log", 'log_file_name', fallback='project.log')

    # log 디렉토리가 없으면 생성한다.
    try:
        os.makedirs(log_dir)
    except OSError:
        if not os.path.isdir(log_dir):
            raise

    #어플리케이션 코드가 직접 사용할 수 있는 인터페이스를 제공함
    logger = logging.getLogger(_logName)

    if log_level == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif log_level == 'WARNING':
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    #logger에 의해 만들어진 log 기록들을 적합한 위치로 보냄
    handler = logging.StreamHandler()

    #log 기록들의 최종 출력본의 레이아웃을 결정함
    formatter = logging.Formatter('[%(asctime)s %(name)s:%(lineno)d] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler('./' + log_dir + '/' + log_file, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("logger module is ready")
    return logger

#logger = setLogging("main")
#logger.info("test")