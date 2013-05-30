import codecs
from pprint import pprint
from genologics.lims import *
from statusDB_utils import *
from genologics.config import BASEURI, USERNAME, PASSWORD
lims = Lims(BASEURI, USERNAME, PASSWORD)
import os
import couchdb
import bcbio.pipeline.config_loader as cl
import time
config_file = os.path.join(os.environ['HOME'], 'opt/config/post_process.yaml')
db_conf = cl.load_config(config_file)['couch_db']        
url = db_conf['maggie_login']+':'+db_conf['maggie_pass']+'@'+db_conf['maggie_url']+':'+str(db_conf['maggie_port']) 
samp_db = couchdb.Server("http://" + url)['samples']

class Lims2DB():
	def get_sample_status():
		"""ongoing,passed,aborted"""

	def get_sequencing(self, proj_name,aplication):
        	SAMPLES = {}
        	runs = lims.get_processes(type = 'Illumina Sequencing (Illumina SBS) 4.0', projectname = proj_name)
        	for run in runs:
        	        run_udfs = dict(run.udf.items())
        	        lanearts=[]
			SEQSTART = run.date_run
			try: SEQFINISH = run_udfs['Finish Date'].isoformat()
			except: SEQFINISH = None
        	        try: 
				inf = run_udfs["Run ID"].split('_') 
				DATE = inf[0]
				FCID = inf[3]
			except: 
				DATE = ''
				FCID = ''
        	        for IOM in run.input_output_maps:
        	                lane_art_id = IOM[0]['limsid']
				lane_art = IOM['uri']
        	                #lane_art = Artifact(lims,id = lane_art_id)
        	                samples = lane_art.samples
        	                if lane_art_id not in lanearts:
        	                        lanearts.append(lane_art_id)
        	                        LANE = lane_art.location[1].split(':')[0]
        	                        for samp in samples:
        	                                if samp.project.name == proj_name:
        	                                        if samp.name not in SAMPLES.keys(): SAMPLES[samp.name] = {}
        	                                        history, id_list = self.get_analyte_hist(lane_art,samp.name)
							print history
        	                                        if history.has_key('39'):
        	                                        	DILPOOLSTART = history['39']['date']
								art = Artifact(lims,id=history['39']['outart'])
        	                                               	BARCODE = self.get_barcode(art.reagent_labels[0])
        	                                              	SAMP_RUN_MET_NAME = '_'.join([LANE,DATE,FCID,BARCODE])
								SAMP_RUN_MET_ID = find_sample_run_id_from_view(samp_db, SAMP_RUN_MET_NAME)
								print aplication
								if history.has_key('47') : key = history['47']['id']
								elif history.has_key('33') : key = history['33']['id']
								elif aplication == 'Finished library' : key = 'Finished'
								if not SAMPLES[samp.name].has_key(key): SAMPLES[samp.name][key] = {}
								SAMPLES[samp.name][key][SAMP_RUN_MET_NAME] = {'dillution_and_pooling_start_date':DILPOOLSTART,
													      'sequencing_start_date':SEQSTART,
													      'sequencing_finish_date':SEQFINISH,
													      'sample_run_metrics_id':SAMP_RUN_MET_ID}
								
        	return SAMPLES

        def get_analyte_hist(self, analyte, sample_name):
                """Makes a historymap of an analyte. sample_name has to be 
                given since the analyte can be a pool of many samples.
                Input:  Analyte instance and related sample name
                Output: List of dicts."""
                hist_pro = {}
                id_list = []
                while analyte:
                        try:
                                pro = analyte.parent_process
                                inarts = analyte.input_artifact_list()
                                for id in inarts:
                                        inart = Artifact(lims, id = id)
                                        for samp in inart.samples:
                                                if samp.name == sample_name:
                                                        the_inart = inart
                                                        break
                                hist_pro[pro.type.id]={'date' : pro.date_run,
                                                        'id' : pro.id,
                                                        'outart' : analyte.id,
                                                        'inart' : the_inart.id}
                                id_list.append(analyte.id)
                                id_list.append(pro.id)
                                analyte = the_inart
                        except:
                                analyte = None
                                pass
                return hist_pro, id_list

	def get_preps(self,application, proj_name):
        	SAMPLES = {}
        	INITALQC_STEPS = ['18','68','65','24','116','9','16','48','66','20','63','7']
        	LIBVAL_STEPS = ['17','62','67','64','8']
        	runs = lims.get_processes(type = 'Aggregate QC (Library Validation) 4.0', projectname = proj_name)
        	for run in runs:
        	        LIBVALSTARTSTEP = run.id
        	        LIBVALFINNISHDATE = run.date_run
        	        LIBVALSTARTDATE = LIBVALFINNISHDATE
        	        for IOM in run.input_output_maps:
        	                art_id = IOM[0]['limsid']
        	                art = Artifact(lims,id = art_id)
        	                samples = art.samples
        	                for samp in samples:
        	                        if samp.project.name == proj_name:
        	                                if samp.name not in SAMPLES.keys(): SAMPLES[samp.name] ={}
        	                                history, id_list = self.get_analyte_hist(art,samp.name)
        	                                ## INITALQC handels DNA and RNA
						if history.has_key('7') or history.has_key('9'):
							try: AggrQC = history['9']
							except: AggrQC = history['7']
        	                                        INITALQCFINNISHDATE = AggrQC['date']
        	                                        INITALQCSTARTDATE = INITALQCFINNISHDATE
        	                                        for step in INITALQC_STEPS:
        	                                                if history.has_key(step):
        	                                                        if int(history[step]['date'].replace('-','')) < int(INITALQCSTARTDATE.replace('-','')):
        	                                                                INITALQCSTARTDATE = history[step]['date']
        	                                        SAMPLES[samp.name]['initial_qc'] = {'start_date':INITALQCSTARTDATE,'finish_date':NITALQCFINNISHDATE }
        	                                ## LIBVALQC
        	                                for step in LIBVAL_STEPS:
        	                                        if history.has_key(step):
        	                                                if int(history[step]['date'].replace('-','')) < int(LIBVALSTARTDATE.replace('-','')):
        	                                                        LIBVALSTARTDATE = history[step]['date']
        	                                ## LIBPREP handels DNA and RNA
        	                                if (history.has_key('47') or history.has_key('33')) and history.has_key('109'):
							try: libPrep = history['47']
							except: libPrep = history['33']
        	                                        if not SAMPLES[samp.name].has_key(libPrep['id']):
        	                                                SAMPLES[samp.name][libPrep['id']] = {'prep_start_date' : libPrep['date'],
													'prep_status' : art.qc_flag,
													'average_size_bp' : dict(art.udf.items())['Size (bp)'],
													'prep_finished_date' : history['109']['date'],
													'library_validation':{}}
							SAMPLES[samp.name][libPrep['id']]['library_validation'][LIBVALSTARTSTEP] = {'start_date': LIBVALSTARTDATE,'finish_date':LIBVALFINNISHDATE}
        	                                elif application == 'Finished library':
        	                                        if not SAMPLES[samp.name].has_key('Finished'): SAMPLES[samp.name]['Finished'] = {'prep_status':art.qc_flag,
																	'average_size_bp':dict(art.udf.items())['Size (bp)'],
																	'library_validation':{}}
        	                                        SAMPLES[samp.name]['Finished']['library_validation'][LIBVALSTARTSTEP] = {'start_date': LIBVALSTARTDATE,'finish_date':LIBVALFINNISHDATE}
        	return SAMPLES


	def get_barcode(self, name):
	        return name.split('(')[1].strip(')')


        def get_prep_leter(self, prep_info):
                """Get preps and prep names; A,B,C... based on prep dates for sample_name. 
                Output: A dict where keys are prep_art_id and values are prep names."""
                dates = {}
		prep_info_new = {}
                preps_keys = map(chr, range(65, 65+len(prep_info)))
                for key, val in prep_info.items():
                        dates[key] = val['prep_start_date']
                for i, key in enumerate(sorted(dates,key= lambda x : dates[x])):
                        prep_info_new[preps_keys[i]] = prep_info[key]
                return prep_info_new


class ProjectDB(Lims2DB):
        """Convert project-udf-fields to project-couchdb-fields"""
        def __init__(self, project_id):
		TT = time.time()
		self.lims_project = Project(lims,id = project_id)
		self.project={'entity_type' : 'project_summary',
			'application' : None,
			'project_name' : self.lims_project.name,
			'project_id' : self.lims_project.id}
                self.udf_field_conv={'Name':'name',
                        #'Queued':'queued',
                        'Portal ID':'Portal_id',
                        'Sample type':'sample_type',
                        'Sequence units ordered (lanes)':'sequence_units_ordered_(lanes)',
                        'Sequencing platform':'sequencing_platform',
                        'Sequencing setup':'sequencing_setup',
                        'Library construction method':'library_construction_method',
                        'Bioinformatics':'bioinformatics',
                        'Disposal of any remaining samples':'disposal_of_any_remaining_samples',
                        'Type of project':'type',
                        'Invoice Reference':'invoice_reference',
                        'Uppmax Project Owner':'uppmax_project_owner',
                        'Custom Capture Design ID':'custom_capture_design_id',
                        'Customer Project Description':'customer_project_description',
                        'Project Comment':'project_comment',
                        'Delivery Report':'delivery_report'}
		self.basic_udf_field_conv = {'Reference genome':'reference_genome',
			'Application':'application',
			'Uppmax Project':'uppnex_id',
			'Customer project reference':'customer_reference'}
                for key, val in self.lims_project.udf.items():
                        if self.udf_field_conv.has_key(key):
                                if self.project.has_key('details'):
                                        self.project['details'][self.udf_field_conv[key]] = val
                                else: self.project['details'] = {self.udf_field_conv[key] : val}
                        elif self.basic_udf_field_conv.has_key(key):
                                self.project[self.basic_udf_field_conv[key]] = val
                self.run_info = self.get_sequencing(self.project['project_name'],self.project['application'])
                self.prepp_info = self.get_preps(self.project['application'],self.project['project_name'])
		samples = lims.get_samples(projectlimsid=self.lims_project.id)
		self.project['no_of_samples'] = len(samples)
		if len(samples) > 0:
			self.project['samples']={}
			for samp in samples:
				samp_run_inf = {}
				samp_prep_inf = {}
				if self.run_info.has_key(samp.name):
					samp_run_inf = self.run_info[samp.name]
				if self.prepp_info.has_key(samp.name):
					samp_prep_inf = self.prepp_info[samp.name]
				sampDB = SampleDB(samp.id, samp_run_inf, samp_prep_inf , self.project['project_name'], self.project['application']) 
				self.project['samples'][sampDB.name] = sampDB.obj
		print time.time() - TT, "projtime"#


class SampleDB(Lims2DB):
        def __init__(self, sample_id, runs, preps, project_name, application = None):
                self.lims_sample = Sample(lims, id = sample_id)
                self.name = self.lims_sample.name
		self.proj = self.lims_sample.project
		self.project_name = project_name
		self.project_application = application
                self.obj={'scilife_name' : self.name}
                self.udf_field_conv = {'Name':'name',
                        'Progress':'progress',
                        'Sequencing Method':'sequencing_method',
                        'Sequencing Coverage':'sequencing_coverage',
                        'Sample Type':'sample_type',
                        'Reference Genome':'reference_genome',
                        'Pooling':'pooling',
                        'Application':'application',
                        'Read Length':'requested_read_length',
                        'Control?':'control',
                        'Sample Buffer':'sample_buffer',
                        'Units':'units',
                        'Customer Volume':'customer_volume',
                        'Color':'color',
                        'Customer Conc.':'customer_conc',
                        'Customer Amount (ug)':'customer_amount_(ug)',
                        'Customer A260:280':'customer_A260:280',
                        'Conc Method':'conc_method',
                        'QC Method':'qc_method',
                        'Extraction Method':'extraction_method',
                        'Customer RIN':'customer_rin',
                        'Sample Links':'sample_links',
                        'Sample Link Type':'sample_link_type',
                        'Tumor Purity':'tumor_purity',
                        'Lanes Requested':'lanes_requested',
                        'Customer nM':'customer_nM',
                        'Customer Average Fragment Length':'customer_average_fragment_length',
                        'Passed Library QC':'prep_status',
                        '-DISCONTINUED-SciLifeLab ID':'sciLifeLab_ID',
			'-DISCONTINUED-Volume Remaining':'volume_remaining'}
		self.basic_udf_field_conv = {'Customer Sample Name':'customer_name',
			'Reads Requested (millions)':'reads_requested_(millions)',
                        'Insert Size':'average_size_bp',
			'Passed Initial QC':'incoming_QC_status'} ## True/False instead of P/NP. OK? 
                for key, val in self.lims_sample.udf.items():
			val = str(val)
			if self.udf_field_conv.has_key(key):
				if self.obj.has_key('details'):
                        		self.obj['details'][self.udf_field_conv[key]] = val
				else: self.obj['details'] = {self.udf_field_conv[key] : val}
			elif self.basic_udf_field_conv.has_key(key):
				self.obj[self.basic_udf_field_conv[key]] = val
		if len(runs) + len(preps) > 0:
			for prep in runs.keys():
				if preps.has_key(prep):
					preps[prep]['sample_run_metrics'] = runs[prep]
			self.obj['library_prep'] = self.get_prep_leter(preps)

