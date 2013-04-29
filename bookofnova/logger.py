# ==============================================================================
# Copyright [2013] [Kevin Carter]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import logging
import os
import sys
from bookofnova.info import __appname__ as appname


class NoLogLevelSet(Exception):
    pass


def logger_setup(log_level, output=sys.stdout):
    """
    Setup logging for your application
    """
    logger = logging.getLogger("%s" % (appname.upper()))
    if log_level.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level.upper() == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level.upper() == 'WARN':
        logger.setLevel(logging.WARN)
    elif log_level.upper() == 'ERROR':
        logger.setLevel(logging.ERROR)
    else:
        raise NoLogLevelSet('I died because you did not set a known log level')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s"
                                  " - %(message)s")

    # Building Handeler
    handler = logging.FileHandler(output)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def return_logfile(filename):
    """
    Return a path for logging file.

    IF "/var/log/" does not exist, or you dont have write permissions to
    "/var/log/" the log file will be in your working directory
    Check for ROOT user if not log to working directory
    """
    if os.path.isfile(filename):
        return filename
    else:
        user = os.getuid()
        logname = ('%s' % filename)
        if not user == 0:
            logfile = logname
        else:
            if os.path.isdir('/var/log'):
                log_loc = '/var/log'
            else:
                try:
                    os.mkdir('%s' % log_loc)
                    logfile = '%s/%s' % (log_loc, logname)
                except Exception:
                    logfile = '%s' % logname
        return logfile
