#!/usr/bin/env python
import galaxy_list

def join_galaxy(conn,table,p,luminosityNorm,normalization,ind,galax):
   
    import sys,string,os,re,MySQLdb,os,string,datetime

    try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
	
        v = cursor.execute('INSERT INTO '+ table + '(voeventid,score,gladeid)'+ ' VALUES('+ 
'(SELECT MAX(id) from voevent_lvc),' + str((p * luminosityNorm / normalization)[ind]) + ',(SELECT id from glade WHERE ra0 =' + str(galax[ind, 0]) + ' AND ' + 'dec0 ='+ str(galax[ind, 1])+ '))') #adds to table
	print v
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  	
