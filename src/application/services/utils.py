import os
import sys
import traceback
from loguru import logger


def set_logger(level):
    ''' 
    Set logger settings with level\n
    To see all the logs, set the level to TRACE; for normal logs set to DEBUG, if you don't want to see those logs, set the level to INFO
    Logger hierarchy+colors:  
    - trace(turquoise), debug(cyan), info(white), critical(purple bg), success(green), warning(yellow), error(red)
    '''
    logger.remove() # remove the default logger
    # Change colors: Critical = [Purple Background], Debug [teal]
    logger.level("CRITICAL", color = "<bold><bg #AF5FD7>")
    logger.level("DEBUG", color="<bold><fg 86>")
    # Format the logger with new settings
    logger.add(sys.stdout, format = "<lvl>{message}</lvl>", colorize=True, backtrace=True, diagnose=True, level=level)  

    
def exception_printer_with_vars(exception, local_vars, loguru_exception=False):
    '''Prints the exception with the **local variable values** at the time of exception'''
    # Log the exception
    logger.critical(f"Exception occurred!")
    logger.error(f'{traceback.format_exc()}')

    # Print all local variables at the point of the exception
    logger.warning("Local variables at the time of exception:")
    for key, value in local_vars.items():
        logger.trace(f"{key}: {value}")
    
    # Raise the exception again to stop the execution
    if loguru_exception:
        logger.exception(exception)
    raise exception
