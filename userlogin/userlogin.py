# --*-- coding:utf-8 --*--

from concurrent import futures
import time
import datetime
import logging
import logging.config
import sys
import grpc
import user_login_pb2
import user_login_pb2_grpc
import gl
import tools
from redisclient import RedisClient
from hbcommon import HBClient
import pbjson
import json
import regionutil


class UserLoginServicerImpl(user_login_pb2_grpc.UserLoginServicer):
    def __init__(self, conf):
        self.logger = logging.getLogger(gl.LOGGERNAME)

        # redis配置
        host = conf.get('redis.host', 'localhost')
        port = conf.getint('redis.port', 6379)
        self.redis = RedisClient(host=host, port=port)

        # hbase 配置
        self.hbase_1 = HBClient()
        # xmd region recognize
        self.regUtil = regionutil.RegionUtil()

        self.telutil = tools.TelUtil(conf=conf)

    def loadSites(self, request, context):

        # 计算时延
        sites = self.redis.getSites()
        res = user_login_pb2.SitesResponse()
        res.sites = sites
        self.logger.info('load site names success')
        return res

    def getCommentsXmdDzdp(self, request, context):

        token = request.token
        site = request.site
        idcard = request.idcard
        pwd = request.pwd

        response = user_login_pb2.ResponseGJJ()
        response.token = token
        response.code = code
        return response


def serve(conf):
    max_workers = conf.get(name='server.threadpool.capacity', defaltValue=50)
    port = conf.getint(name='server.port', defaltValue=50051)

    logger = logging.getLogger(gl.LOGGERNAME)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    user_login_pb2_grpc.add_UserLoginServicer_to_server(UserLoginServicerImpl(conf), server)
    server.add_insecure_port('[::]:%s' % port)
    server.start()
    logger.info('server started, listening on  %s' % port)

    try:
        while True:
            time.sleep(gl.ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    fname = None
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        print sys.stderr, 'err: python userlogin.py ./conf/server.conf'
        exit(1)

    conf = tools.Config(fname=fname)
    logPath = conf.get(name='logs.conf.path', defaltValue='./conf/logging.conf')
    print 'logs conf path:', logPath
    logging.config.fileConfig(logPath)
    serve(conf)
