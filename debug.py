import sys
import os
import codecs
from pprint import pprint
from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD
import objectsDB as DB
import couchdb
import bcbio.pipeline.config_loader as cl


config_file = os.path.join(os.environ['HOME'], 'opt/config/post_process.yaml')
db_conf = cl.load_config(config_file)['couch_db']
url = db_conf['maggie_login']+':'+db_conf['maggie_pass']+'@'+db_conf['maggie_url']+':'+str(db_conf['maggie_port'])
couch = couchdb.Server("http://" + url)
lims = Lims(BASEURI, USERNAME, PASSWORD)


proj_name='M.Uhlen_13_01'

proj_db = couch['analysis']#projects']
proj = lims.get_projects(name = proj_name)[0]
obj = DB.ProjectDB(proj.id)
obj.obj['_id'] = find_or_make_key(proj_db, proj.name)
obj.obj['samples']={'P414_123':obj.obj['samples']['P414_123']}
info = save_couchdb_obj(proj_db, obj.obj)

sample_run='6_121207_AD1H19ACXX_AGTTCC'
samp_db=couch['samples']
find_sample_run_id_from_view(samp_db,sample_run)
