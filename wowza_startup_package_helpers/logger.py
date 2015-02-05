import os
import datetime

class LogEntry(object):
    def __init__(self, level, message):
        self.dt = datetime.datetime.now()
        self.level = level
        self.message = message
    def __str__(self):
        dtstr = self.dt.isoformat()
        lvl = self.level
        def build_line(line):
            return '%s\t%s\t%s\n' % (dtstr, lvl, line.strip('\n'))
        return ''.join([build_line(line) for line in self.message.splitlines()])
        
class Logger(object):
    log_dir = os.path.getcwd()
    log_filename = 'startup_package_helper.log'
    def __init__(self):
        self.info('LOG START')
    @property
    def log_path(self):
        return os.path.join(self.log_dir, self.log_filename)
    def _write_log(self, entry):
        with open(self.log_path, 'a') as f:
            f.write(str(entry))
    def log(self, message, level=None):
        if level is None:
            level = 'INFO'
        e = LogEntry(level, message)
        self._write_log(e)
    def info(self, message):
        self.log(message, 'INFO')
    def warn(self, message):
        self.log(message, 'WARN')
    def error(self, message):
        self.log(message, 'ERROR')
    def debug(self, message):
        self.log(message, 'DEBUG')
        
logger = Logger()
    
    
