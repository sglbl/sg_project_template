import os
import re
import sys
import base64
import traceback
from pathlib import Path
from loguru import logger
from overrides import EnforceOverrides


def set_logger(level="TRACE", write_to_file=False, remove_file_if_exists=True):
    ''' 
    Set logger settings with level\n
    To see all the logs, set the level to TRACE; for normal logs set to DEBUG, if you don't want to see those logs, set the level to INFO
    Logger hierarchy+colors:  
    - trace(turquoise), debug(cyan), info(white), critical(purple bg), success(green), warning(yellow), error(red)
    '''
    logger.remove() # remove the default logger
    # Adding new levels: Critical = Text with Purple Background, Title: Light 
    logger.level("CRITICAL", color = "<bold><bg #AF5FD7>")
    try:
        logger.level("TITLE")
    except ValueError:
        logger.level("TITLE", color="<bold><fg 86>", no=21)
    
    # Format the logger with new settings
    logger.add(sys.stdout, format = "<lvl>{message}</lvl>", colorize=True, backtrace=True, diagnose=True, level=level)  
    if write_to_file:
        # remove the file if it exists
        if remove_file_if_exists:
            Path("/tmp/app_logs.log").unlink(missing_ok=True)
        logger.add("/tmp/app_logs.log", format = "<lvl>{message}</lvl>", colorize=True, level=level)
    

def exception_printer_with_vars(exception, local_vars, loguru_exception=False):
    '''Prints the exception with the **local variable values** at the time of exception'''
    # Log the exception
    logger.critical(f"Exception occurred!")
    logger.error(f'{traceback.format_exc()}')

    # Print all local variables at the point of the exception
    logger.warning("Local variables at the time of exception:")
    for key, value in local_vars.items():
        logger.debug(f"{key}: {value}")
    
    # Raise the exception again to stop the execution
    if loguru_exception:
        logger.exception(exception)
    raise exception


def refresh_db():
    # remove content of 'data/chroma_data/'
    db_dir = "./data/outputs/"
    file = "database.db"
    path = os.path.join(db_dir, file)
    if os.path.exists(path):
        os.remove(path)


class Interface(EnforceOverrides):
    """Interface class to:
        1. Prevent instantiation of the interface / abstract class (without using typing.Protocol)
        2. Make sure that all abstract class methods are overridden in the subclass (without using abc.@abstractmethod)
        3. Make sure to put @override decorator on all the overridden methods in the subclass (using overrides.EnforceOverrides)
        4. Make sure that all subclass methods exist in the abstract class with the same method signatures
    """
    
    def __new__(cls, *args, **kwargs):
        # Prevent direct instantiation of Interface or its direct subclasses
        if cls is Interface or Interface in cls.__bases__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__}")
        # Check if all methods are overridden
        for name, method in cls.__bases__[0].__dict__.items():
            if callable(method) and not name.startswith("__"):  # Exclude special methods
                if name not in cls.__dict__ or cls.__dict__[name] == method:
                    raise TypeError(f"Subclass {cls.__name__} must override the method '{name}'")
        return super().__new__(cls)
