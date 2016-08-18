#!/usr/bin/env python
import galaxy_list


def join_lvc_voevent(conn,table,values):

    import sys,string,os,re,MySQLdb,os,string,datetime

    datecreated_tables = ['atels','groups','iaunames','instruments','notes',
                          'obsrequests','photlco','photlcoraw','photpairing',
                          'spec','speclcoraw','targetnames','targets',
                          'telescopes','useractionlog','users']
    if 'datecreated' not in values and table in datecreated_tables:
        values['datecreated'] = str(datetime.datetime.utcnow())

    def dictValuePad(key):
        return '%(' + str(key) + ')s'

    def insertFromDict(table, dicto):
        """Take dictionary object dict and produce sql for 
        inserting it into the named table"""
        cleandict = {key: val for key, val in dicto.items() if val not in ['NaN', 'UNKNOWN', 'N/A', None, '']}

        sql = 'INSERT INTO ' + table
        sql += ' ('
        sql += ', '.join(cleandict)
        sql += ') VALUES ('
        sql += ', '.join(map(dictValuePad, cleandict))
        sql += ');'
        print sql
        return sql

    sql = insertFromDict(table, values)
    
    try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute(sql, values)
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
def join_galaxy(conn,table,p,luminosityNorm,normalization,ind,galax):
   
    import sys,string,os,re,MySQLdb,os,string,datetime
    try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
	
        v = cursor.execute('INSERT INTO lvc_galaxies(voeventid,score,gladeid)'+ ' VALUES('+ 
'(SELECT MAX(id) from voevent_lvc),' + str((p * luminosityNorm / normalization)[ind]) + ',(SELECT id from glade WHERE ra0 =' + str(galax[ind, 0]) + ' AND ' + 'dec0 ='+ str(galax[ind, 1])+ '))') #adds to table
	print v
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  


	
