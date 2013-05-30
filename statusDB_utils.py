#!/usr/bin/env python
from uuid import uuid4
import time
from  datetime  import  datetime

def find_or_make_key(proj_db, project_name):
    key = find_proj_from_view(proj_db, project_name)
    if not key: 
	key = uuid4().hex
    return key

def save_couchdb_obj(db, obj):
    dbobj = db.get(obj['_id'])
    time_log = datetime.utcnow().isoformat() + "Z"
    if dbobj is None:
        obj["creation_time"] = time_log
        obj["modification_time"] = time_log
        db.save(obj)
        return 'Created'
    else:
        obj["_rev"] = dbobj.get("_rev")
        del dbobj["modification_time"]
        obj["creation_time"] = dbobj["creation_time"]
        if not comp_obj(obj, dbobj):
            obj["modification_time"] = time_log
            db.save(obj)
            return 'Uppdated'
    return None

def comp_obj(obj, dbobj):
        for key in dbobj:
                if (obj.has_key(key)):
                        if (obj[key] != dbobj[key]):
                             return False
                else:
                        return False
        return True

def find_proj_from_view(proj_db, project_name):
        view = proj_db.view('project/project_name')
        for proj in view:
                if proj.key == project_name:
                        return proj.value
        return None

def find_samp_from_view(samp_db, proj_name):
        view = samp_db.view('names/id_to_proj')
        samps = {}
        for doc in view:
                if (doc.value[0] == proj_name)|(doc.value[0] == proj_name.lower()):
                        samps[doc.key] = doc.value[1:3]
        return samps

def find_flowcell_from_view(flowcell_db, flowcell_name):
	view = flowcell_db.view('names/id_to_name')
        for doc in view:
                if doc.value.split('_')[1] == flowcell_name:
                        return doc.key

def find_sample_run_id_from_view(samp_db,sample_run):
	view = samp_db.view('names/id_to_name')
	for doc in view:
		K = doc.key
		V = doc.value
		if V == sample_run:
     			return K
	return None


