-- ----------------------------
-- View structure for qa_flags
-- ----------------------------
DROP VIEW IF EXISTS "public"."qa_flags";
CREATE VIEW "public"."qa_flags" AS  SELECT qa.result_id,
    string_agg((( SELECT qat.quality_assurance
           FROM mercury_qualityassurancetype qat
          WHERE (qat.id = qa.quality_assurance_id)))::text, ','::text) AS qa_flags,
    string_agg((( SELECT qat.nwis_value_qualifier
           FROM mercury_qualityassurancetype qat
          WHERE (qat.id = qa.quality_assurance_id)))::text, ''::text) AS nwis_flags,
    string_agg(( SELECT qat.nwis_value_qualifier_comment
           FROM mercury_qualityassurancetype qat
          WHERE (qat.id = qa.quality_assurance_id)), ';'::text) AS nwis_comments
   FROM mercury_qualityassurance qa
  GROUP BY qa.result_id;

-- ----------------------------
-- View structure for depth
-- ----------------------------
DROP VIEW IF EXISTS "public"."depth";
CREATE VIEW "public"."depth" AS  SELECT sample.id AS sample_integer,
    '00098'::text AS parameter_cd,
    (sample.depth)::text AS result_value,
    NULL::text AS remark_cd,
    NULL::text AS qa_cd,
    NULL::text AS qw_method_cd,
    NULL::text AS results_rd,
    NULL::text AS val_qual_cd,
    NULL::double precision AS rpt_lev_value,
    NULL::text AS rpt_lev_cd,
    NULL::text AS dqi_cd,
    NULL::text AS null_val_qual,
    NULL::text AS prep_set_no,
    NULL::text AS anl_set_no,
    NULL::text AS anl_dt,
    NULL::text AS prep_dt,
    NULL::text AS lab_result_comment,
    NULL::text AS field_result_comment,
    NULL::text AS lab_std_dev,
    'USGSWIML'::text AS anl_ent,
    min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text)) AS entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM (((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE ((sample.depth IS NOT NULL) AND (sample.depth <> ALL (ARRAY[('-999'::integer)::double precision, (0)::double precision])) AND (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL)))
  GROUP BY sample.id, sample.depth, project.name
  ORDER BY sample.id, '00098'::text, sample.depth, (min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text))), 'USGSWIML'::text;

-- ----------------------------
-- View structure for report_internal_bottles_site_names
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_internal_bottles_site_names";
CREATE VIEW "public"."report_internal_bottles_site_names" AS  SELECT mercury_site.name,
    mercury_bottle.bottle_unique_name,
    mercury_sample.sample_date_time
   FROM (((mercury_samplebottle
     JOIN mercury_sample ON ((mercury_samplebottle.sample_id = mercury_sample.id)))
     JOIN mercury_site ON ((mercury_sample.site_id = mercury_site.id)))
     JOIN mercury_bottle ON ((mercury_samplebottle.bottle_id = mercury_bottle.id)));

-- ----------------------------
-- View structure for report_internal_constituents_per_month_by_project
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_internal_constituents_per_month_by_project";
CREATE VIEW "public"."report_internal_constituents_per_month_by_project" AS  SELECT max((project.name)::text) AS "Project Name",
    max((project.accounting_code)::text) AS "USGS PROJECT ACCOUNTING CODE",
    max((const.constituent)::text) AS "Parameter",
    to_char((sample.received_date)::timestamp with time zone, 'Mon-YY'::text) AS "Month Received At Lab",
    count(res.id) AS "Total number of parameters logged into  database",
    to_char(min(sample.sample_date_time), 'MM/DD/YYYY'::text) AS "Earliest sample collection date",
    to_char(max(sample.sample_date_time), 'MM/DD/YYYY'::text) AS "Latest sample collection date"
   FROM (((((((((mercury_result res
     LEFT JOIN qa_flags ON ((res.id = qa_flags.result_id)))
     LEFT JOIN mercury_constituenttype const ON ((res.constituent_id = const.id)))
     LEFT JOIN mercury_methodtype meth ON ((res.method_id = meth.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((res.sample_bottle_id = sampbot.id)))
     LEFT JOIN mercury_bottle bottle ON ((sampbot.bottle_id = bottle.id)))
     LEFT JOIN mercury_sample sample ON ((sampbot.sample_id = sample.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
  WHERE (sample.received_date >= '2019-10-01'::date)
  GROUP BY project.name, const.constituent, sample.received_date
  ORDER BY const.constituent, sample.received_date;

-- ----------------------------
-- View structure for report_internal_raw_values
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_internal_raw_values";
CREATE VIEW "public"."report_internal_raw_values" AS  SELECT site.name AS "Site",
    site.usgs_scode AS "USGS Station ID",
    sample.sample_date_time AS "Sample Date Time",
    medium.medium AS "Medium",
        CASE
            WHEN (((sample.length)::character varying)::text = '-999'::text) THEN 'NA'::character varying
            ELSE (sample.length)::character varying
        END AS "Sample Length (m)",
    sample.depth AS "Sample Depth (m)",
    res.analyzed_date AS "Analysis Date",
    res.id AS "Results ID",
    bottle.bottle_unique_name AS "Bottle ID",
    const.constituent AS "Parameter",
    res.final_daily_detection_limit AS "DDL (output)",
    det.detection_flag AS "D-Flag (output)",
    res.raw_value AS "Raw Value",
    unit.unit AS "Units",
    sample.id AS "Field ID",
    res.analysis_comment AS "Analysis Comment",
    sample.comment AS "Sample Comment",
    qa_flags.qa_flags AS "ALL QA FLAGS"
   FROM ((((((((((mercury_result res
     LEFT JOIN qa_flags ON ((res.id = qa_flags.result_id)))
     LEFT JOIN mercury_constituenttype const ON ((res.constituent_id = const.id)))
     LEFT JOIN mercury_methodtype meth ON ((res.method_id = meth.id)))
     LEFT JOIN mercury_unittype unit ON ((meth.final_value_unit_id = unit.id)))
     LEFT JOIN mercury_detectionflag det ON ((res.detection_flag_id = det.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((res.sample_bottle_id = sampbot.id)))
     LEFT JOIN mercury_bottle bottle ON ((sampbot.bottle_id = bottle.id)))
     LEFT JOIN mercury_sample sample ON ((sampbot.sample_id = sample.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
  WHERE ((sample.project_id = 6264) AND ((res.entry_date >= '2014-11-08'::date) AND (res.entry_date <= '2014-11-30'::date)))
  ORDER BY site.name, sample.sample_date_time;

-- ----------------------------
-- View structure for report_nawqa_results_count
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_nawqa_results_count";
CREATE VIEW "public"."report_nawqa_results_count" AS  SELECT project.name AS project_name,
    substr((site.name)::text, 1, 4) AS site_name,
    res.entry_date,
    row_number() OVER () AS row_num
   FROM ((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE (((project.name)::text ~~ 'NAWQA HG%'::text) AND (res.analyzed_date IS NOT NULL))
  ORDER BY project.name, (substr((site.name)::text, 1, 4));

-- ----------------------------
-- View structure for report_nwis_results
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_nwis_results";
CREATE VIEW "public"."report_nwis_results" AS  SELECT sample.id AS sample_integer,
    meth.nwis_parameter_code AS parameter_cd,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN '#'::text
            ELSE (res.report_value)::text
        END AS result_value,
        CASE
            WHEN (((det.detection_flag)::text <> ('<'::character varying(128))::text) AND ((det.detection_flag)::text <> ('E'::character varying(128))::text)) THEN NULL::character varying(128)
            ELSE det.detection_flag
        END AS remark_cd,
    'H'::text AS qa_cd,
    NULL::text AS qw_method_cd,
    NULL::text AS results_rd,
    qa_flags.qa_flags AS val_qual_cd,
        CASE
            WHEN (res.final_method_detection_limit IS NOT NULL) THEN res.final_method_detection_limit
            WHEN (meth.method_detection_limit IS NOT NULL) THEN meth.method_detection_limit
            ELSE NULL::double precision
        END AS rpt_lev_value,
        CASE
            WHEN (res.final_method_detection_limit IS NOT NULL) THEN 'MDL'::text
            WHEN (meth.method_detection_limit IS NOT NULL) THEN 'MDL'::text
            ELSE NULL::text
        END AS rpt_lev_cd,
    NULL::text AS dqi_cd,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN 'c'::text
            ELSE NULL::text
        END AS null_val_qual,
    NULL::text AS prep_set_no,
    NULL::text AS anl_set_no,
    to_char((res.analyzed_date)::timestamp with time zone, 'YYYYMMDD'::text) AS anl_dt,
    NULL::text AS prep_dt,
    concat(sample.comment,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN qa_flags.nwis_comments
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN concat(';', qa_flags.nwis_comments)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('Filter type: ', filt.filter)
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('; Filter type: ', filt.filter)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NULL) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('Bottle ID: ', bottle.bottle_unique_name)
            WHEN (((((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) OR (filt.filter IS NOT NULL)) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('; Bottle ID: ', bottle.bottle_unique_name)
            ELSE NULL::text
        END) AS lab_result_comment,
    NULL::text AS field_result_comment,
    NULL::text AS lab_std_dev,
    'USGSWIML'::text AS anl_ent,
    res.entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM ((((((((((mercury_result res
     LEFT JOIN qa_flags ON ((res.id = qa_flags.result_id)))
     LEFT JOIN mercury_methodtype meth ON ((res.method_id = meth.id)))
     LEFT JOIN mercury_detectionflag det ON ((res.detection_flag_id = det.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((res.sample_bottle_id = sampbot.id)))
     LEFT JOIN mercury_bottle bottle ON ((sampbot.bottle_id = bottle.id)))
     LEFT JOIN mercury_filtertype filt ON ((sampbot.filter_type_id = filt.id)))
     LEFT JOIN mercury_sample sample ON ((sampbot.sample_id = sample.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
  WHERE (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL))
  ORDER BY sample.id, meth.nwis_parameter_code,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN '#'::text
            ELSE (res.report_value)::text
        END,
        CASE
            WHEN (((det.detection_flag)::text <> ('<'::character varying(128))::text) OR ((det.detection_flag)::text <> ('E'::character varying(128))::text)) THEN NULL::character varying(128)
            ELSE det.detection_flag
        END, 'H'::text, NULL::text, qa_flags.qa_flags,
        CASE
            WHEN (meth.method_detection_limit = (0)::double precision) THEN NULL::double precision
            ELSE meth.method_detection_limit
        END,
        CASE
            WHEN (meth.method_detection_limit = (0)::double precision) THEN NULL::text
            WHEN (meth.method_detection_limit IS NULL) THEN NULL::text
            ELSE 'MDL'::text
        END,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN 'c'::text
            ELSE NULL::text
        END, (to_char((res.analyzed_date)::timestamp with time zone, 'YYYYMMDD'::text)), (concat(sample.comment,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN qa_flags.nwis_comments
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN concat(';', qa_flags.nwis_comments)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('Filter type: ', filt.filter)
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('; Filter type: ', filt.filter)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NULL) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('Bottle ID: ', bottle.bottle_unique_name)
            WHEN (((((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) OR (filt.filter IS NOT NULL)) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('; Bottle ID: ', bottle.bottle_unique_name)
            ELSE NULL::text
        END)), 'USGSWIML'::text;

-- ----------------------------
-- View structure for report_nwis_results_ld
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_nwis_results_ld";
CREATE VIEW "public"."report_nwis_results_ld" AS ( SELECT sample.id AS sample_integer,
    meth.nwis_parameter_code AS parameter_cd,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN '#'::text
            ELSE (res.report_value)::text
        END AS result_value,
        CASE
            WHEN (((det.detection_flag)::text <> ('<'::character varying(128))::text) AND ((det.detection_flag)::text <> ('E'::character varying(128))::text)) THEN NULL::character varying(128)
            ELSE det.detection_flag
        END AS remark_cd,
    'H'::text AS qa_cd,
    NULL::text AS qw_method_cd,
    NULL::text AS results_rd,
    qa_flags.qa_flags AS val_qual_cd,
        CASE
            WHEN (res.final_method_detection_limit IS NOT NULL) THEN res.final_method_detection_limit
            WHEN (meth.method_detection_limit IS NOT NULL) THEN meth.method_detection_limit
            ELSE NULL::double precision
        END AS rpt_lev_value,
        CASE
            WHEN (res.final_method_detection_limit IS NOT NULL) THEN 'MDL'::text
            WHEN (meth.method_detection_limit IS NOT NULL) THEN 'MDL'::text
            ELSE NULL::text
        END AS rpt_lev_cd,
    NULL::text AS dqi_cd,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN 'c'::text
            ELSE NULL::text
        END AS null_val_qual,
    NULL::text AS prep_set_no,
    NULL::text AS anl_set_no,
    to_char((res.analyzed_date)::timestamp with time zone, 'YYYYMMDD'::text) AS anl_dt,
    NULL::text AS prep_dt,
    concat(sample.comment,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN qa_flags.nwis_comments
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN concat(';', qa_flags.nwis_comments)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('Filter type: ', filt.filter)
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('; Filter type: ', filt.filter)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NULL) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('Bottle ID: ', bottle.bottle_unique_name)
            WHEN (((((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) OR (filt.filter IS NOT NULL)) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('; Bottle ID: ', bottle.bottle_unique_name)
            ELSE NULL::text
        END) AS lab_result_comment,
    NULL::text AS field_result_comment,
    NULL::text AS lab_std_dev,
    'USGSWIML'::text AS anl_ent,
    res.entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM ((((((((((mercury_result res
     LEFT JOIN qa_flags ON ((res.id = qa_flags.result_id)))
     LEFT JOIN mercury_methodtype meth ON ((res.method_id = meth.id)))
     LEFT JOIN mercury_detectionflag det ON ((res.detection_flag_id = det.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((res.sample_bottle_id = sampbot.id)))
     LEFT JOIN mercury_bottle bottle ON ((sampbot.bottle_id = bottle.id)))
     LEFT JOIN mercury_filtertype filt ON ((sampbot.filter_type_id = filt.id)))
     LEFT JOIN mercury_sample sample ON ((sampbot.sample_id = sample.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
  WHERE (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL))
  ORDER BY sample.id, meth.nwis_parameter_code,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN '#'::text
            ELSE (res.report_value)::text
        END,
        CASE
            WHEN (((det.detection_flag)::text <> ('<'::character varying(128))::text) OR ((det.detection_flag)::text <> ('E'::character varying(128))::text)) THEN NULL::character varying(128)
            ELSE det.detection_flag
        END, 'H'::text, NULL::text, qa_flags.qa_flags,
        CASE
            WHEN (meth.method_detection_limit = (0)::double precision) THEN NULL::double precision
            ELSE meth.method_detection_limit
        END,
        CASE
            WHEN (meth.method_detection_limit = (0)::double precision) THEN NULL::text
            WHEN (meth.method_detection_limit IS NULL) THEN NULL::text
            ELSE 'MDL'::text
        END,
        CASE
            WHEN (((res.report_value)::text = '-999'::text) OR ((res.report_value)::text = '-999.0'::text)) THEN 'c'::text
            ELSE NULL::text
        END, (to_char((res.analyzed_date)::timestamp with time zone, 'YYYYMMDD'::text)), (concat(sample.comment,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN qa_flags.nwis_comments
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) THEN concat(';', qa_flags.nwis_comments)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('Filter type: ', filt.filter)
            WHEN (((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text)) AND (filt.filter IS NOT NULL)) THEN concat('; Filter type: ', filt.filter)
            ELSE NULL::text
        END,
        CASE
            WHEN (((sample.comment IS NULL) OR (sample.comment = ''::text)) AND ((qa_flags.nwis_comments IS NULL) OR (qa_flags.nwis_comments = ''::text)) AND (filt.filter IS NULL) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('Bottle ID: ', bottle.bottle_unique_name)
            WHEN (((((sample.comment IS NOT NULL) OR (sample.comment <> ''::text)) AND ((qa_flags.nwis_comments IS NOT NULL) OR (qa_flags.nwis_comments <> ''::text))) OR (filt.filter IS NOT NULL)) AND (bottle.bottle_unique_name IS NOT NULL)) THEN concat('; Bottle ID: ', bottle.bottle_unique_name)
            ELSE NULL::text
        END)), 'USGSWIML'::text)
UNION
( SELECT sample.id AS sample_integer,
    '00098'::text AS parameter_cd,
    (sample.depth)::text AS result_value,
    NULL::text AS remark_cd,
    NULL::text AS qa_cd,
    NULL::text AS qw_method_cd,
    NULL::text AS results_rd,
    NULL::text AS val_qual_cd,
    NULL::double precision AS rpt_lev_value,
    NULL::text AS rpt_lev_cd,
    NULL::text AS dqi_cd,
    NULL::text AS null_val_qual,
    NULL::text AS prep_set_no,
    NULL::text AS anl_set_no,
    NULL::text AS anl_dt,
    NULL::text AS prep_dt,
    NULL::text AS lab_result_comment,
    NULL::text AS field_result_comment,
    NULL::text AS lab_std_dev,
    'USGSWIML'::text AS anl_ent,
    min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text)) AS entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM (((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE ((sample.depth IS NOT NULL) AND (sample.depth <> ALL (ARRAY[('-999'::integer)::double precision, (0)::double precision])) AND (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL)))
  GROUP BY sample.id, sample.depth, project.name
  ORDER BY sample.id, '00098'::text, sample.depth, (min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text))), 'USGSWIML'::text)
UNION
( SELECT sample.id AS sample_integer,
    '00024'::text AS parameter_cd,
    ((sample.length * (39.37)::double precision))::text AS result_value,
    NULL::text AS remark_cd,
    NULL::text AS qa_cd,
    NULL::text AS qw_method_cd,
    NULL::text AS results_rd,
    NULL::text AS val_qual_cd,
    NULL::double precision AS rpt_lev_value,
    NULL::text AS rpt_lev_cd,
    NULL::text AS dqi_cd,
    NULL::text AS null_val_qual,
    NULL::text AS prep_set_no,
    NULL::text AS anl_set_no,
    NULL::text AS anl_dt,
    NULL::text AS prep_dt,
    NULL::text AS lab_result_comment,
    NULL::text AS field_result_comment,
    NULL::text AS lab_std_dev,
    'USGSWIML'::text AS anl_ent,
    min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text)) AS entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM (((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE ((sample.length IS NOT NULL) AND (sample.length <> ALL (ARRAY[('-999'::integer)::double precision, (0)::double precision])) AND (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL)))
  GROUP BY sample.id, sample.length, project.name
  ORDER BY sample.id, '00024'::text, sample.length, (min(to_date(to_char((res.entry_date)::timestamp with time zone, 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text))), 'USGSWIML'::text);

-- ----------------------------
-- View structure for report_nwis_samples
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_nwis_samples";
CREATE VIEW "public"."report_nwis_samples" AS  SELECT sample.id AS sample_integer,
    site.nwis_customer_code AS user_code,
    'USGS'::text AS agency_cd,
        CASE
            WHEN (site.usgs_scode IS NULL) THEN site.name
            ELSE site.usgs_scode
        END AS site_no,
    concat(to_char((sample.sample_date_time)::timestamp with time zone, 'YYYYMMDD'::text), lpad(to_char((sample.sample_date_time)::timestamp with time zone, 'HH24MI'::text), 4, '0'::text)) AS sample_start_date,
    NULL::text AS sample_end_date,
        CASE
            WHEN (sample.replicate > 1) THEN medium.nwis_code_qa
            ELSE medium.nwis_code
        END AS medium_cd,
    NULL::text AS lab_id,
    NULL::text AS project_cd,
    NULL::text AS aqfr_cd,
    NULL::text AS sample_type,
    NULL::text AS anl_start_cd,
    NULL::text AS anl_src_cd,
    NULL::text AS hyd_cond_cd,
    NULL::text AS hyd_event_cd,
    NULL::text AS tissue_id,
    NULL::text AS body_part_cd,
    NULL::text AS lab_smp_comment,
    replace(replace(
        CASE
            WHEN ((project.accounting_code IS NULL) OR ((project.accounting_code)::text = ''::text)) THEN
            CASE
                WHEN ((sample.comment IS NULL) OR (sample.comment = ''::text)) THEN concat('Project Name: ', project.name)
                ELSE concat(replace(sample.comment, '\s+'::text, '   '::text), '; Project Name: ', project.name)
            END
            ELSE concat(
            CASE
                WHEN ((sample.comment IS NULL) OR (sample.comment = ''::text)) THEN concat('Project Name: ', project.name)
                ELSE concat(replace(sample.comment, '\s+'::text, '   '::text), '; Project Name: ', project.name)
            END, '\\', project.accounting_code)
        END, chr(13), ''::text), chr(10), ''::text) AS field_smp_comment,
    NULL::text AS sample_tz_cd,
    NULL::text AS tm_datum_rlblty_cd,
    NULL::text AS coll_agency_cd,
    res.entry_date,
    project.name AS project_name,
    row_number() OVER () AS row_num
   FROM ((((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_filtertype filt ON ((sampbot.filter_type_id = filt.id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE (((medium.medium)::text !~~ 'EXP%'::text) AND (sample.project_id <> 962) AND (sample.project_id <> 963) AND ((site.name)::text <> 'BLANK'::text) AND ((site.nwis_customer_code IS NOT NULL) AND ((site.nwis_customer_code)::text <> ''::text)) AND (res.method_id <> ALL (ARRAY[98, 67, 74, 77, 87, 89, 93, 94, 184, 188])) AND (res.isotope_flag_id = 11) AND ((res.report_value)::text <> '-888.0'::text) AND (res.final_value IS NOT NULL))
  ORDER BY sample.id, site.nwis_customer_code, 'USGS'::text,
        CASE
            WHEN (site.usgs_scode IS NULL) THEN site.name
            ELSE site.usgs_scode
        END, (concat(to_char((sample.sample_date_time)::timestamp with time zone, 'YYYYMMDD'::text), lpad(to_char((sample.sample_date_time)::timestamp with time zone, 'HH24MI'::text), 4, '0'::text))), NULL::text,
        CASE
            WHEN (sample.replicate > 1) THEN medium.nwis_code_qa
            ELSE medium.nwis_code
        END, (replace(replace(
        CASE
            WHEN ((project.accounting_code IS NULL) OR ((project.accounting_code)::text = ''::text)) THEN
            CASE
                WHEN ((sample.comment IS NULL) OR (sample.comment = ''::text)) THEN concat('Project Name: ', project.name)
                ELSE concat(replace(sample.comment, '\s+'::text, '   '::text), '; Project Name: ', project.name)
            END
            ELSE concat(
            CASE
                WHEN ((sample.comment IS NULL) OR (sample.comment = ''::text)) THEN concat('Project Name: ', project.name)
                ELSE concat(replace(sample.comment, '\s+'::text, '   '::text), '; Project Name: ', project.name)
            END, '\\', project.accounting_code)
        END, chr(13), ''::text), chr(10), ''::text));

-- ----------------------------
-- View structure for report_projects_results_count
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_projects_results_count";
CREATE VIEW "public"."report_projects_results_count" AS  SELECT project.name AS project_name,
    site.nwis_customer_code,
    NULL::text AS "null",
    coop.email AS cooperator_email,
    res.entry_date,
    row_number() OVER () AS row_num
   FROM (((((mercury_sample sample
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_cooperator coop ON ((project.cooperator_id = coop.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((sample.id = sampbot.sample_id)))
     LEFT JOIN mercury_result res ON ((res.sample_bottle_id = sampbot.id)))
  WHERE (res.analyzed_date IS NOT NULL)
  ORDER BY project.name, site.nwis_customer_code;

-- ----------------------------
-- View structure for report_cooperator_results
-- ----------------------------
DROP VIEW IF EXISTS "public"."report_cooperator_results";
CREATE VIEW "public"."report_cooperator_results" AS  SELECT site.name AS site_name,
    site.usgs_scode,
    sample.sample_date_time,
    medium.medium,
        CASE
            WHEN (((sample.length)::character varying)::text = '-999'::text) THEN 'NA'::character varying
            ELSE (sample.length)::character varying
        END AS length,
    sample.depth,
    res.analyzed_date AS analysis_date,
    res.id AS result_id,
    bottle.bottle_unique_name AS bottle,
    const.constituent,
    res.final_daily_detection_limit AS final_ddl,
    det.detection_flag,
    res.percent_matching,
    res.final_value,
    unit.unit,
    sample.id AS sample_id,
    res.analysis_comment,
    sample.comment AS sample_comment,
    qa_flags.qa_flags AS qaflags,
    res.entry_date,
    project.name AS project_name,
    coop.name AS cooperator_name,
    row_number() OVER () AS row_num
   FROM ((((((((((((mercury_result res
     LEFT JOIN qa_flags ON ((res.id = qa_flags.result_id)))
     LEFT JOIN mercury_constituenttype const ON ((res.constituent_id = const.id)))
     LEFT JOIN mercury_methodtype meth ON ((res.method_id = meth.id)))
     LEFT JOIN mercury_unittype unit ON ((meth.final_value_unit_id = unit.id)))
     LEFT JOIN mercury_detectionflag det ON ((res.detection_flag_id = det.id)))
     LEFT JOIN mercury_samplebottle sampbot ON ((res.sample_bottle_id = sampbot.id)))
     LEFT JOIN mercury_bottle bottle ON ((sampbot.bottle_id = bottle.id)))
     LEFT JOIN mercury_sample sample ON ((sampbot.sample_id = sample.id)))
     LEFT JOIN mercury_mediumtype medium ON ((sample.medium_type_id = medium.id)))
     LEFT JOIN mercury_site site ON ((sample.site_id = site.id)))
     LEFT JOIN mercury_project project ON ((sample.project_id = project.id)))
     LEFT JOIN mercury_cooperator coop ON ((project.cooperator_id = coop.id)))
  ORDER BY site.name, sample.sample_date_time;
