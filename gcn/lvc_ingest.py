import socket
import struct
import time

# Prefer lxml.etree over xml.etree (it's faster)
try:
    import lxml.etree
    import io
    def parse_from_string(text):
        return lxml.etree.parse(io.BytesIO(text)).getroot()
    from lxml.etree import XMLSyntaxError
except ImportError:
    import xml.etree.cElementTree
    parse_from_string = xml.etree.cElementTree.fromstring
    try:
        from xml.etree.cElementTree import ParseError as XMLSyntaxError
    except ImportError: # Python 2.6 raises a different exception
        from xml.parsers.expat import ExpatError as XMLSyntaxError
import logging
import datetime
import base64
import urllib
import voeventparse as vp
import os
import galaxy_list
import json
import MySQLdb

with open('/supernova/configure.json') as f:
    conn = MySQLdb.connect(*json.load(f))

def insert_values(table, dict_to_insert):
    keys = dict_to_insert.keys()
    vals = [str(dict_to_insert[key]) for key in keys]
    query = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ', '.join(keys), ', '.join(vals))
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, dict_to_insert)
    resultSet = cursor.fetchall()
    conn.commit()
    cursor.close()

def lvc_insert(root, payload):
    ivorn = root.attrib['ivorn']
    filename = urllib.quote_plus(ivorn)
    with open(filename, "w") as f:
        f.write(payload)
        logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)
    with open(filename) as f:
        v = vp.load(f)

###################################################################################LVC ONLY#############################################################################  
    if "LVC" in ivorn: 
        
        dict1 = {}
        #Parameters
        paramlist = ['packet_type','pkt_ser_num','alert_type','graceid',
'id_letter','trig_id','trigger_tjd','trigger_sod','eventpage','search','pipeline','internal','far','chirpmass','eta','maxdistance','trigger_id','misc_flags',
'lvc_internal','test','retraction','internal_test','num_det_participated','lho_participated','llo_participated','virgo_participated','geo600_participated',
'kagra_participated','lio_participated','sequence_number','_group','probhasns','probhasremnant','hardwareinj','vetted','openalert','temporalcoinc']

        valuelist = ['Packet_Type','Pkt_Ser_Num','AlertType','GraceID','ID_Letter','TrigID','Trigger_TJD','Trigger_SOD',
'EventPage','Search','Pipeline','Internal','FAR','ChirpMass','ETA','MaxDistance','Trigger_ID','Misc_flags',
'LVC_Internal','Test','Retraction','InternalTest','Num_Det_participated','LHO_participated',
'LLO_participated','Virgo_participated','GEO600_participated','KAGRA_participated','LIO_participated','Sequence_number',
'Group','ProbHasNS','ProbHasRemnant','HardwareInj','Vetted','OpenAlert','TemporalCoinc']


        dict1 = {key: (v.find(".//Param[@name='"+ value +"']").attrib['value'] if v.find(".//Param[@name='"+ value +"']") is not None else None) for key, value in zip(paramlist, valuelist)}

        dict1.update({'skymap_url_fits_basic': ""})

        keylist1 = ['ivorn','role','version'] 
        
        for key in keylist1:
                dict1[key] = v.attrib[key]
        #Source
        dict1.update({'author_ivorn': v.Who.AuthorIVORN,'shortname': v.Who.Author.shortName,'contactname': v.Who.Author.contactName,'contactemail': v.Who.Author.contactEmail,'date': v.Who.Date,'who_description': v.Who.Description})
    
        #xmlns
        dict1.update({'xmlns_voe': "http://www.ivoa.net/xml/VOEvent/v2.0",'xmlns_xsi': "http://www.w3.org/2001/XMLSchema-instance",'xsi_schemalocation': "http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"})

       

        #ObservationInfo                
        dict1.update({'observatorylocation_id': v.WhereWhen.ObsDataLocation.ObservatoryLocation.attrib['id'],'astrocoordsystem_id': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem.attrib['id'],'timeunit': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.attrib['unit'],'isotime': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime,'how_description': v.How.Description,'reference_uri': 'http://gcn.gsfc.nasa.gov/gcn/ligo.html','importance': v.Why.attrib['importance'],'inference_probability': v.Why.Inference.attrib['probability'],'concept': v.Why.Inference.Concept})

        
        #to act on both Initial and Update notices
        if v.find(".//Param[@name='AlertType']").attrib['value'] == "Initial" or v.find(".//Param[@name='AlertType']").attrib['value'] == "Update" :
            dict1.update({'skymap_url_fits_basic': v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value']}) 

        #insert into table
        insert_values("voevent_lvc", dict1)

        if (v.find(".//Param[@name='AlertType']").attrib['value'] == "Initial" or v.find(".//Param[@name='AlertType']").attrib['value'] == "Update") and not v.find(".//Param[@name='ID_Letter']").attrib['value'] == "M" : #remove 'and not v.find(".//Param[@name='ID_Letter']").attrib['value'] == "M"' in order to save LVC M-series (or test events that occur every 10 min) to lvc_galaxies table

            #wget command
            command = 'wget --auth-no-challenge ' + v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value'] + ' -O' + ' /supernova/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz'

            #print command 
            os.system(command)
            
            #fetch FITS file
            galaxy_map = galaxy_list.find_galaxy_list('/supernova/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz') 

            #print galaxy_map #prints out the coordinates in form [RA, DEC, Distance to obj(in Mpc), Bmag, probability score]

        else:
            pass       
#######################################################################LVC ONLY ^#########################################################################       
    elif "ICECUBE" in ivorn:
     
        keylist1 = ['ivorn','role','version'] 
        dict1 = {}
        for key in keylist1:
                dict1[key] = v.attrib[key]
        #Source
        dict1.update({'author_ivorn': v.Who.AuthorIVORN,'shortname': v.Who.Author.shortName,'contactname': v.Who.Author.contactName,'contactemail': v.Who.Author.contactEmail,'date': v.Who.Date,'who_description': v.Who.Description})
    
        #xmlns
        dict1.update({'xmlns_voe': "http://www.ivoa.net/xml/VOEvent/v2.0",'xmlns_xsi': "http://www.w3.org/2001/XMLSchema-instance",'xsi_schemalocation': "http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"})

        #parameters
        dict1.update({'packet_type': v.find(".//Param[@name='Packet_Type']").attrib['value'],'pkt_ser_num': v.find(".//Param[@name='Pkt_Ser_Num']").attrib['value'],'trig_id': v.find(".//Param[@name='TrigID']").attrib['value'],'event_tjd': v.find(".//Param[@name='Event_TJD']").attrib['value'],'event_sod': v.find(".//Param[@name='Event_SOD']").attrib['value'],'nevents': v.find(".//Param[@name='Nevents']").attrib['value'],'stream': v.find(".//Param[@name='Stream']").attrib['value'],'rev': v.find(".//Param[@name='Rev']").attrib['value'],'false_pos': v.find(".//Param[@name='False_pos']").attrib['value'],'pvalue': v.find(".//Param[@name='pvalue']").attrib['value'],'deltat': v.find(".//Param[@name='deltaT']").attrib['value'],'sigmat': v.find(".//Param[@name='sigmaT']").attrib['value'],'charge': v.find(".//Param[@name='charge']").attrib['value'],'signalness': v.find(".//Param[@name='signalness']").attrib['value'],'hesetypeindex': v.find(".//Param[@name='hesetypeindex']").attrib['value'],'trigger_id': v.find(".//Param[@name='Trigger_ID']").attrib['value'],'misc_flags': v.find(".//Param[@name='Misc_flags']").attrib['value'],'subtype': v.find(".//Param[@name='SubType']").attrib['value'],'test': v.find(".//Param[@name='Test']").attrib['value'],'radec_valid': v.find(".//Param[@name='RADec_valid']").attrib['value'],'retraction': v.find(".//Param[@name='Retraction']").attrib['value'],'internal_test': v.find(".//Param[@name='InternalTest']").attrib['value']})

        #ObservationInfo                
        dict1.update({'observatorylocation_id': v.WhereWhen.ObsDataLocation.ObservatoryLocation.attrib['id'],'astrocoordsystem_id': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem.attrib['id'],'timeunit': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.attrib['unit'],'isotime': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime,'ra0': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C1,'dec0': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C2,'error2radius': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Error2Radius, 'how_description': v.How.Description,'reference_uri': 'http://gcn.gsfc.nasa.gov/gcn/ligo.html','importance': v.Why.attrib['importance'],'inference_probability': v.Why.Inference.attrib['probability'],'concept': v.Why.Inference.Concept})

        #insert into table
        insert_values("voevent_amon", dict1)
    else:
        pass
    print "DONE"
    #os.system("rm " + filename) #uncomment if you want received voevents to be removed from archive after program runs


