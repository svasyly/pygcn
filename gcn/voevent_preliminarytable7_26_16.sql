CREATE TABLE `voevent_lvc` (
  `voevent_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ivorn` text NOT NULL,
  `role` varchar(45) NOT NULL,
  `version` text NOT NULL,
  `xmlns_voe` text NOT NULL,
  `xmlns_xsi` text NOT NULL,
  `xsi_schemalocation` text NOT NULL,
  `author_ivorn` text NOT NULL,
  `shortname` text,
  `contactname` text,
  `contactemail` text,
  `who_description` text,
  `date` text NOT NULL,
  `packet_type` text NOT NULL,
  `pkt_ser_num` text NOT NULL,
  `alert_type` text NOT NULL,
  `graceid` text NOT NULL,
  `id_letter` text NOT NULL,
  `trig_id` text NOT NULL,
  `trigger_tjd` text NOT NULL,
  `trigger_sod` text NOT NULL,
  `eventpage` text NOT NULL,
  `_group` text NOT NULL,
  `search` varchar(45) NOT NULL,
  `pipeline` varchar(45) NOT NULL,
  `internal` varchar(45) NOT NULL,
  `far` text NOT NULL,
  `chirpmass` text NOT NULL,
  `eta` text NOT NULL,
  `maxdistance` text NOT NULL,
  `trigger_id` varchar(45) NOT NULL,
  `misc_flags` varchar(45) DEFAULT NULL,
  `lvc_internal` text,
  `test` varchar(45) DEFAULT NULL,
  `retraction` varchar(45) DEFAULT NULL,
  `internal_test` varchar(45) DEFAULT NULL,
  `num_det_participated` text NOT NULL,
  `lho_participated` varchar(45) NOT NULL,
  `llo_participated` varchar(45) NOT NULL,
  `virgo_participated` varchar(45) NOT NULL,
  `geo600_participated` varchar(45) NOT NULL,
  `kagra_participated` varchar(45) NOT NULL,
  `lio_participated` varchar(45) NOT NULL,
  `sequence_number` text NOT NULL,
  `observatorylocation_id` text NOT NULL,
  `astrocoordsystem_id` text NOT NULL,
  `timeunit` varchar(45) NOT NULL,
  `isotime` text NOT NULL,
  `how_description` text,
  `reference_uri` text,
  `importance` text DEFAULT NULL,
  `inference_probability` text DEFAULT NULL,
  `concept` text,
  `datecreated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `lastmodified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`lvc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
