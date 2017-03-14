import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-7s %(asctime)s]  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('xweb')
