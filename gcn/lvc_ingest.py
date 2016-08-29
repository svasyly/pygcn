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
import join_table
import lsc
import voeventparse as vp

def lvc_insert(root, payload):
    ivorn = root.attrib['ivorn']
    filename = urllib.quote_plus(ivorn)
    with open(filename, "w") as f:
	f.write(payload)
	logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)
    with open(filename) as f:
	v = vp.load(f)
    v
###################################################################################LVC ONLY################################################################################
    #To act on Preliminary Notices	
    if "LVC" in ivorn: 
	
        keylist1 = ['ivorn','role','version'] 
    	dict1 = {}
        for key in keylist1:
    	    dict1[key] = v.attrib[key]
        #Source
        dict1.update({'author_ivorn': v.Who.AuthorIVORN,'shortname': v.Who.Author.shortName,'contactname': v.Who.Author.contactName,'contactemail': v.Who.Author.contactEmail,'date': v.Who.Date,'who_description': v.Who.Description})
    
        #xmlns
        dict1.update({'xmlns_voe': "http://www.ivoa.net/xml/VOEvent/v2.0",'xmlns_xsi': "http://www.w3.org/2001/XMLSchema-instance",'xsi_schemalocation': "http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"})

        #Parameters
        dict1.update({'packet_type': v.find(".//Param[@name='Packet_Type']").attrib['value'],'pkt_ser_num': v.find(".//Param[@name='Pkt_Ser_Num']").attrib['value'],'alert_type': v.find(".//Param[@name='AlertType']").attrib['value'],'graceid': v.find(".//Param[@name='GraceID']").attrib['value'],'id_letter': v.find(".//Param[@name='ID_Letter']").attrib['value'],'trig_id': v.find(".//Param[@name='TrigID']").attrib['value'],'trigger_tjd': v.find(".//Param[@name='Trigger_TJD']").attrib['value'],'trigger_sod': v.find(".//Param[@name='Trigger_SOD']").attrib['value'],'eventpage': v.find(".//Param[@name='EventPage']").attrib['value'],'search': v.find(".//Param[@name='Search']").attrib['value'],'pipeline': v.find(".//Param[@name='Pipeline']").attrib['value'],'internal': v.find(".//Param[@name='Internal']").attrib['value'],'far': v.find(".//Param[@name='FAR']").attrib['value'],'chirpmass': v.find(".//Param[@name='ChirpMass']").attrib['value'],'eta': v.find(".//Param[@name='Eta']").attrib['value'],'maxdistance': v.find(".//Param[@name='MaxDistance']").attrib['value'],'trigger_id': v.find(".//Param[@name='Trigger_ID']").attrib['value'],'misc_flags': v.find(".//Param[@name='Misc_flags']").attrib['value'],'lvc_internal': v.find(".//Param[@name='LVC_Internal']").attrib['value'],'test': v.find(".//Param[@name='Test']").attrib['value'],'retraction': v.find(".//Param[@name='Retraction']").attrib['value'],'internal_test': v.find(".//Param[@name='InternalTest']").attrib['value'],'num_det_participated': v.find(".//Param[@name='Num_Det_participated']").attrib['value'],'lho_participated': v.find(".//Param[@name='LHO_participated']").attrib['value'],'llo_participated': v.find(".//Param[@name='LLO_participated']").attrib['value'],'virgo_participated': v.find(".//Param[@name='Virgo_participated']").attrib['value'],'geo600_participated': v.find(".//Param[@name='GEO600_participated']").attrib['value'],'kagra_participated': v.find(".//Param[@name='KAGRA_participated']").attrib['value'],'lio_participated': v.find(".//Param[@name='LIO_participated']").attrib['value'],'sequence_number': v.find(".//Param[@name='Sequence_number']").attrib['value'],'_group': v.find(".//Param[@name='Group']").attrib['value'],'skymap_url_fits_basic': ""})

        #ObservationInfo		
        dict1.update({'observatorylocation_id': v.WhereWhen.ObsDataLocation.ObservatoryLocation.attrib['id'],'astrocoordsystem_id': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem.attrib['id'],'timeunit': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.attrib['unit'],'isotime': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime,'how_description': v.How.Description,'reference_uri': 'http://gcn.gsfc.nasa.gov/gcn/ligo.html','importance': v.Why.attrib['importance'],'inference_probability': v.Why.Inference.attrib['probability'],'concept': v.Why.Inference.Concept})

        
        #to act on both Initial and Update Notices
	if v.find(".//Param[@name='AlertType']").attrib['value'] == "Initial" or v.find(".//Param[@name='AlertType']").attrib['value'] == "Update" :
            dict1.update({'skymap_url_fits_basic': v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value']}) 
	    print dict1 

        #insert into table
        hostname, username, passwd, database = lsc.mysqldef.getconnection("lcogt2")
        conn = lsc.mysqldef.dbConnect(hostname, username, passwd, database)
	lsc.mysqldef.insert_values(conn, "voevent_lvc", dict1)

	if v.find(".//Param[@name='AlertType']").attrib['value'] == "Initial" or v.find(".//Param[@name='AlertType']").attrib['value'] == "Update" :
	    import galaxy_list
	    #wget command
	    import os
	    command = 'wget --auth-no-challenge ' + v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value'] + ' -O' + ' /home/svasylyev/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz'

	    #print command 
	    os.system(command)
	    import galaxy_list
	    galaxy_map = galaxy_list.find_galaxy_list('/home/svasylyev/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz')

	    print galaxy_map #prints out the coordinates in form [RA, DEC, Distance to obj(in Mpc), Bmag, probability score]

	else:
	    pass	      
    elif "ICECUBE" in ivorn:
   	print "AMON ALERT"
	keylist1 = ['ivorn','role','version'] 
    	dict1 = {}
        for key in keylist1:
    	    dict1[key] = v.attrib[key]
        #Source
        dict1.update({'author_ivorn': v.Who.AuthorIVORN,'shortname': v.Who.Author.shortName,'contactname': v.Who.Author.contactName,'contactemail': v.Who.Author.contactEmail,'date': v.Who.Date,'who_description': v.Who.Description})
    
        #xmlns
        dict1.update({'xmlns_voe': "http://www.ivoa.net/xml/VOEvent/v2.0",'xmlns_xsi': "http://www.w3.org/2001/XMLSchema-instance",'xsi_schemalocation': "http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"})

	#parameters
	dict1.update({'packet_type': v.find(".//Param[@name='Packet_Type']").attrib['value'],'pkt_ser_num': v.find(".//Param[@name='Pkt_Ser_Num']").attrib['value'],'trig_id': v.find(".//Param[@name='TrigID']").attrib['value'],'event_tjd': v.find(".//Param[@name='Event_TJD']").attrib['value'],'nevents': v.find(".//Param[@name='Nevents']").attrib['value'],'stream': v.find(".//Param[@name='Stream']").attrib['value'],'rev': v.find(".//Param[@name='Rev']").attrib['value'],'false_pos': v.find(".//Param[@name='False_pos']").attrib['value'],'pvalue': v.find(".//Param[@name='pvalue']").attrib['value'],'deltat': v.find(".//Param[@name='deltaT']").attrib['value'],'sigmat': v.find(".//Param[@name='sigmaT']").attrib['value'],'charge': v.find(".//Param[@name='charge']").attrib['value'],'signalness': v.find(".//Param[@name='signalness']").attrib['value'],'hesetypeindex': v.find(".//Param[@name='hesetypeindex']").attrib['value'],'trigger_id': v.find(".//Param[@name='Trigger_ID']").attrib['value'],'misc_flags': v.find(".//Param[@name='Misc_flags']").attrib['value'],'subtype': v.find(".//Param[@name='SubType']").attrib['value'],'test': v.find(".//Param[@name='Test']").attrib['value'],'radec_valid': v.find(".//Param[@name='RADec_valid']").attrib['value'],'retraction': v.find(".//Param[@name='Retraction']").attrib['value'],'internal_test': v.find(".//Param[@name='InternalTest']").attrib['value']})

	#ObservationInfo		
        dict1.update({'observatorylocation_id': v.WhereWhen.ObsDataLocation.ObservatoryLocation.attrib['id'],'astrocoordsystem_id': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem.attrib['id'],'timeunit': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.attrib['unit'],'isotime': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime,'ra0': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C1,'dec0': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C2,'error2radius': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Error2Radius, 'how_description': v.How.Description,'reference_uri': 'http://gcn.gsfc.nasa.gov/gcn/ligo.html','importance': v.Why.attrib['importance'],'inference_probability': v.Why.Inference.attrib['probability'],'concept': v.Why.Inference.Concept})
        print dict1
	hostname, username, passwd, database = lsc.mysqldef.getconnection("lcogt2")
	conn = lsc.mysqldef.dbConnect(hostname, username, passwd, database)
	lsc.mysqldef.insert_values(conn, "voevent_amon", dict1)
#################################################################################LVC#################################################################################################   

