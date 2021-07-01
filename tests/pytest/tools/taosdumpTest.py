###################################################################
#           Copyright (c) 2016 by TAOS Technologies, Inc.
#                     All rights reserved.
#
#  This file is proprietary and confidential to TAOS Technologies.
#  No part of this file may be reproduced, stored, transmitted,
#  disclosed or used in any form or by any means other than as
#  expressly provided by the written permission from Jianhui Tao
#
###################################################################

# -*- coding: utf-8 -*-

import sys
import os
from util.log import *
from util.cases import *
from util.sql import *
from util.dnodes import *


class TDTestCase:
    def init(self, conn, logSql):
        tdLog.debug("start to execute %s" % __file__)
        tdSql.init(conn.cursor(), logSql)
        
        self.ts = 1538548685000
        self.numberOfTables = 10000
        self.numberOfRecords = 100

    def run(self):
        if not os.path.exists("/taosdumptest/tmp1"):
            os.makedirs("/taosdumptest/tmp1")
        else:
            print("目录存在")
        if not os.path.exists("/taosdumptest/tmp2"):
            os.makedirs("/taosdumptest/tmp2")        
        tdSql.execute("drop database if exists db")
        tdSql.execute("create database db  days 11 keep 3649 blocks 8 ")
        tdSql.execute("create database db1  days 12 keep 3640 blocks 7 ")
        tdSql.execute("use db")
        tdSql.execute("create table st(ts timestamp, c1 int, c2 nchar(10)) tags(t1 int, t2 binary(10))")
        tdSql.execute("create table t1 using st tags(1, 'beijing')")        
        sql = "insert into t1 values"
        currts = self.ts
        for i in range(100):
            sql += "(%d, %d, 'nchar%d')" % (currts + i, i % 100, i % 100)
        tdSql.execute(sql)
        tdSql.execute("create table t2 using st tags(2, 'shanghai')")        
        sql = "insert into t2 values"
        currts = self.ts
        for i in range(100):
            sql += "(%d, %d, 'nchar%d')" % (currts + i, i % 100, i % 100)
        tdSql.execute(sql)

        os.system("rm /tmp/*.sql")
        os.system("taosdump --databases db -o /taosdumptest/tmp1")
        os.system("taosdump --databases db1 -N -o /taosdumptest/tmp2")
       
        tdSql.execute("drop database db")
        tdSql.execute("drop database db1")
        tdSql.query("show databases")
        tdSql.checkRows(0)
        os.system("taosdump -i /taosdumptest/tmp1")
        os.system("taosdump -i /taosdumptest/tmp2")

        tdSql.execute("use db")
        tdSql.query("show databases")
        tdSql.checkRows(2)
        dbresult = tdSql.queryResult
        # 6--days,7--keep0,keep1,keep, 12--block,
        for i in  range(len(dbresult)):
            if dbresult[i][0] == 'db':
                print(dbresult[i])
                print(type(dbresult[i][6]))
                print(type(dbresult[i][7]))
                print(type(dbresult[i][9]))
                assert dbresult[i][6] == 11
                assert dbresult[i][7] == "3649,3649,3649"
                assert dbresult[i][9] == 8
            if dbresult[i][0] == 'db1':
                assert dbresult[i][6] == 10
                assert dbresult[i][7] == "3650,3650,3650"
                assert dbresult[i][9] == 6

        tdSql.query("show stables")
        tdSql.checkRows(1)
        tdSql.checkData(0, 0, 'st')

        tdSql.query("show tables")
        tdSql.checkRows(2)
        tdSql.checkData(0, 0, 't2')
        tdSql.checkData(1, 0, 't1')

        tdSql.query("select * from t1")
        tdSql.checkRows(100)
        for i in range(100):
            tdSql.checkData(i, 1, i)
            tdSql.checkData(i, 2, "nchar%d" % i)

        tdSql.query("select * from t2")
        tdSql.checkRows(100)
        for i in range(100):
            tdSql.checkData(i, 1, i)
            tdSql.checkData(i, 2, "nchar%d" % i)

        # drop all databases，boundary value testing. length(databasename)<=32;length(tablesname)<=192
        tdSql.execute("drop database db")
        tdSql.execute("drop database db1")
        os.system("rm -rf /taosdumptest/tmp1")
        os.system("rm -rf /taosdumptest/tmp2")    
        os.makedirs("/taosdumptest/tmp1")
        tdSql.execute("create database db12312313231231321312312312_323")     
        tdSql.error("create database db12312313231231321312312312_3231")     
        tdSql.execute("use db12312313231231321312312312_323")
        tdSql.execute("create stable st12345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678_9(ts timestamp, c1 int, c2 nchar(10)) tags(t1 int, t2 binary(10))")
        tdSql.error("create stable st_12345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678_9(ts timestamp, c1 int, c2 nchar(10)) tags(t1 int, t2 binary(10))")
        tdSql.execute("create stable st(ts timestamp, c1 int, c2 nchar(10)) tags(t1 int, t2 binary(10))")
        tdSql.error("create stable st1(ts timestamp, c1 int, col2_012345678901234567890123456789012345678901234567890123456789 nchar(10)) tags(t1 int, t2 binary(10))")

        tdSql.execute("select * from db12312313231231321312312312_323.st12345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678_9")   
        tdSql.error("create table t0_12345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678912345678_9 using st tags(1, 'beijing')")  
        tdSql.query("show stables")
        tdSql.checkRows(2)
        os.system("taosdump --databases db12312313231231321312312312_323 -o /taosdumptest/tmp1")
        tdSql.execute("drop database db12312313231231321312312312_323")       
        os.system("taosdump -i /taosdumptest/tmp1")
        tdSql.execute("use db12312313231231321312312312_323")
        tdSql.query("show stables")
        tdSql.checkRows(2)
        os.system("rm -rf /taosdumptest/tmp1")
        os.system("rm -rf /taosdumptest/tmp2") 
        os.system("rm -rf ./dump_result.txt")
        os.system("rm -rf ./db.csv")      
      

    def stop(self):
        tdSql.close()
        tdLog.success("%s successfully executed" % __file__)


tdCases.addWindows(__file__, TDTestCase())
tdCases.addLinux(__file__, TDTestCase())