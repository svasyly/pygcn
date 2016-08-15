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
    if v.find(".//Param[@name='AlertType']").attrib['value'] == "Preliminary": 
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

        #print dict1
        hostname, username, passwd, database = lsc.mysqldef.getconnection("lcogt2")
        conn = lsc.mysqldef.dbConnect(hostname, username, passwd, database)
	#for item in diclist:
        #lsc.mysqldef.insert_values(conn, "glade_catalog", item)
	join_table.join_lvc_voevent(conn, "voevent_lvc", dict1)
	header = ['ra0', 'dec0', 'dist', 'bmag', 'bt_hyp', 'e_bt_hyp', 'it_hyp', 'e_it_hyp', 'modz_hyp', 'mod0_hyp', 'logd25_hyp', 'e_logd25_hyp', 'logr25_hyp', 'e_logr25_hyp', 'logdc_hyp', 'pa_hyp', 'btc_hyp', 'itc_hyp', 'ubtc_hyp', 'bvtc_hyp', 'jmag_2mass', 'errjmag_2mass', 'hmag_2mass', 'errhmag_2mass', 'kmag_2mass', 'errkmag_2mass', 'ab_ratio_2mass', 'pa_in_kmag_2mass', 'bmag_gwgc', 'majdiam_gwgc', 'errmd_gwgc', 'mindiam_gwgc', 'errmid_gwgc', 'pa_gwgc', 'dist_gwgc', 'errdist_gwgc', 'errbmag_gwgc', 'kmag_2mpz', 'errkmag_2mpz', 'bmag_2mpz', 'errbmag_2mpz', 'errbmag_2_2mpz', 'zspec_2mpz', 'zphot_2mpz', 'errzphot_2mpz', 'errzphot_2_2mpz', 'flag']
	f = open('/home/svasylyev/Downloads/GLADE_1.2.txt')
	#counter = 0
	#limit = 100
	#diclist = []
#header = ['ra0','dec0','dist','bmag','bt_hyp','e_bt_hyp','it_hyp','e_it_hyp','modz_hyp','mod0_hyp','logd25_hyp','e_logd25_hyp','logr25_hyp','e_logr25_hyp','logdc_hyp','']
	#for line in f:
            #counter += 1
	    #print counter
    	    #dic = {}
    	    #if counter == limit: break
    	    #for i in range(len(header)):
        	#dic.update({header[i]: line.split()[i]})
    	  #lsc.mysqldef.insert_values(conn, "glade_catalog", dic)
	
            
    #The following is to act on both Initial and Update Notices
    elif v.find(".//Param[@name='AlertType']").attrib['value'] == "Initial" or v.find(".//Param[@name='AlertType']").attrib['value'] == "Update" :
    	keylist1 = ['ivorn','role','version']
    	dict1 = {}
        for key in keylist1:
    	    dict1[key] = v.attrib[key]
        #Source
        dict1.update({'author_ivorn': v.Who.AuthorIVORN,'shortname': v.Who.Author.shortName,'contactname': v.Who.Author.contactName,'contactemail': v.Who.Author.contactEmail,'date': v.Who.Date,'who_description': v.Who.Description})
    
        #xmlns
        dict1.update({'xmlns_voe': "http://www.ivoa.net/xml/VOEvent/v2.0",'xmlns_xsi': "http://www.w3.org/2001/XMLSchema-instance",'xsi_schemalocation': "http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"})

        #Parameters
        dict1.update({'packet_type': v.find(".//Param[@name='Packet_Type']").attrib['value'],'pkt_ser_num': v.find(".//Param[@name='Pkt_Ser_Num']").attrib['value'],'alert_type': v.find(".//Param[@name='AlertType']").attrib['value'],'graceid': v.find(".//Param[@name='GraceID']").attrib['value'],'id_letter': v.find(".//Param[@name='ID_Letter']").attrib['value'],'trig_id': v.find(".//Param[@name='TrigID']").attrib['value'],'trigger_tjd': v.find(".//Param[@name='Trigger_TJD']").attrib['value'],'trigger_sod': v.find(".//Param[@name='Trigger_SOD']").attrib['value'],'eventpage': v.find(".//Param[@name='EventPage']").attrib['value'],'search': v.find(".//Param[@name='Search']").attrib['value'],'pipeline': v.find(".//Param[@name='Pipeline']").attrib['value'],'internal': v.find(".//Param[@name='Internal']").attrib['value'],'far': v.find(".//Param[@name='FAR']").attrib['value'],'chirpmass': v.find(".//Param[@name='ChirpMass']").attrib['value'],'eta': v.find(".//Param[@name='Eta']").attrib['value'],'maxdistance': v.find(".//Param[@name='MaxDistance']").attrib['value'],'trigger_id': v.find(".//Param[@name='Trigger_ID']").attrib['value'],'misc_flags': v.find(".//Param[@name='Misc_flags']").attrib['value'],'lvc_internal': v.find(".//Param[@name='LVC_Internal']").attrib['value'],'test': v.find(".//Param[@name='Test']").attrib['value'],'retraction': v.find(".//Param[@name='Retraction']").attrib['value'],'internal_test': v.find(".//Param[@name='InternalTest']").attrib['value'],'num_det_participated': v.find(".//Param[@name='Num_Det_participated']").attrib['value'],'lho_participated': v.find(".//Param[@name='LHO_participated']").attrib['value'],'llo_participated': v.find(".//Param[@name='LLO_participated']").attrib['value'],'virgo_participated': v.find(".//Param[@name='Virgo_participated']").attrib['value'],'geo600_participated': v.find(".//Param[@name='GEO600_participated']").attrib['value'],'kagra_participated': v.find(".//Param[@name='KAGRA_participated']").attrib['value'],'lio_participated': v.find(".//Param[@name='LIO_participated']").attrib['value'],'sequence_number': v.find(".//Param[@name='Sequence_number']").attrib['value'],'_group': v.find(".//Param[@name='Group']").attrib['value'], 'skymap_url_fits_basic': v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value']})

        #ObservationInfo		
        dict1.update({'observatorylocation_id': v.WhereWhen.ObsDataLocation.ObservatoryLocation.attrib['id'],'astrocoordsystem_id': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoordSystem.attrib['id'],'timeunit': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.attrib['unit'],'isotime': v.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime,'how_description': v.How.Description,'reference_uri': 'http://gcn.gsfc.nasa.gov/gcn/ligo.html','importance': v.Why.attrib['importance'],'inference_probability': v.Why.Inference.attrib['probability'],'concept': v.Why.Inference.Concept})
    
	import galaxy_list
	
        #print dict1
        hostname, username, passwd, database = lsc.mysqldef.getconnection("lcogt2")
        conn = lsc.mysqldef.dbConnect(hostname, username, passwd, database)
        #lsc.mysqldef.insert_values(conn, "voevent_lvc", dict1)
	join_table.join_lvc_voevent(conn, "voevent_lvc", dict1)
	

	#wget command
	import os
	command = 'wget --auth-no-challenge ' + v.find(".//Param[@name='SKYMAP_URL_FITS_BASIC']").attrib['value'] + ' -O' + ' /home/svasylyev/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz'

	#print command 
	os.system(command)
	import galaxy_list
	galaxy_map = galaxy_list.find_galaxy_list('/home/svasylyev/ligoevent_fits/' + v.find(".//Param[@name='GraceID']").attrib['value'] + '_' + v.find(".//Param[@name='AlertType']").attrib['value'] + '.fits.gz')
	print galaxy_map #prints out the coordinates in form [RA, DEC, Distance to obj(in Mpc), Bmag, probability score]
    else:
   	print "Unknown Alert Type"
   

