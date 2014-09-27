from datetime import datetime
import os
from pprint import pprint
import sys
# import redis
# from config import REDIS_SERVER_URL,REDIS_PORT, REDIS_DB

class logger(object):
    def __init__(self, logdir, fname, insertDate= False):
        self.start_time = datetime.now()
        
        # check if the log dir path exists
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        self.module_name = fname
        if insertDate:
            self.LOGFILE_PATH = os.path.join(logdir , fname + '.' + str(datetime.now()) + '.log')
        else:
            self.LOGFILE_PATH = os.path.join(logdir , fname + '.log')
        self.LOGFILE = open(self.LOGFILE_PATH, 'a')
        print 'logfile initiated at : ' + self.LOGFILE_PATH

        # print 'connecting to redis'
        # self.rc = redis.StrictRedis(host=REDIS_SERVER_URL, port=REDIS_PORT, db=0)


    def log(self, log_str, class_name=''):
        # print '[%s||%s] %s' % (str(datetime.now()), class_name, log_str)
        self.LOGFILE.write('[' + str(datetime.now()) + '||' + class_name + '] ' + str(log_str) + '\n')
        
    """This method is for pretty printing the log 
    """
    def plog(self, log_str, class_name=''):
        # pprint('[%s||%s] %s' % (str(datetime.now()), class_name, log_str))
        # self.LOGFILE.write('[' + str(datetime.now()) + '||' + class_name + '] ' + str(log_str) + '\n')
        str1 = '%s | %s | %s | %s \n' %(datetime.now(), self.module_name, class_name, log_str )
        print str1
        sys.stdout.flush()
        #print str1;
        self.LOGFILE.write(str1)
        self.LOGFILE.flush()