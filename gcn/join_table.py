#!/usr/bin/env python
import galaxy_list


def join_lvc_voevent(conn,table,values):
    #for element in galaxylist:
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
	#v = cursor.execute('INSERT INTO lvc_galaxies(voevent_id)'+
#' SELECT MAX(voevent_id) from voevent_lvc')
	#cursor.execute('INSERT INTO lvc galaxies(score)' + (p * luminosityNorm / normalization)[ind]))
	#cursor.execute('INSERT INTO lvc_galaxies(score) ' + 'VALUES('+ str((p * luminosityNorm / normalization)[ind]) +')')
        #print v
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
	
        v = cursor.execute('INSERT INTO lvc_galaxies(voevent_id,score,glade_id)'+ ' VALUES('+ 
'(SELECT MAX(voevent_id) from voevent_lvc),' + str((p * luminosityNorm / normalization)[ind]) + ',(SELECT glade_id from glade_catalog WHERE ra0 =' + str(galax[ind, 0]) + ' AND ' + 'dec0 ='+ str(galax[ind, 1])+ '))')
	print v
        #cursor.execute('INSERT INTO lvc_galaxies(score) ' + 'VALUES('+ str((p * luminosityNorm / normalization)[ind]) +')')
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  

        #conn.commet()
        #cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  
def join_score(conn,table,p,luminosityNorm,normalization,ind):
   
    import sys,string,os,re,MySQLdb,os,string,datetime
    try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        
        cursor.execute('INSERT INTO lvc_galaxies(score) ' + 'VALUES('+ str((p * luminosityNorm / normalization)[ind]) +')')
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  

        #conn.commet()
        #cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])  

	
