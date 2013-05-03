import codecs
from pprint import pprint
from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD
lims = Lims(BASEURI, USERNAME, PASSWORD)

art1=Artifact(lims,id='2-20293')
print art1.udf.items()

"""
The output will be a list of udfs with corespond to the udfs found in the api:
https://genologics-stage.scilifelab.se:8443/api/v2/artifacts/2-20293

We then create a nothe artifact instacne with a nother id:
"""

art2=Artifact(lims,id='2-16304')
print art2.udf.items()


"""
The outhput is the same as in art1.udf.items(), but if we look in the api for this second artifact the udfs are not the same:

https://genologics-stage.scilifelab.se:8443/api/v2/artifacts/2-16304

If you restart python and create art2 before art1 then art1 will get the udfs of art2.

The problem is the same when creating two process instances and comparing the input_output_maps"""

pro1=Process(lims,id='24-1258')
pro2=Process(lims,id='24-1271')

pro1.input_output_maps[0]
pro2.input_output_maps[0]


"""
compare to:
https://genologics-stage.scilifelab.se:8443/api/v2/processes/24-1271
and
https://genologics-stage.scilifelab.se:8443/api/v2/processes/24-1258



The issues are solved by commenting out

        #try:
        #    return self.value
        #except AttributeError:

in 
class UdfDictionaryDescriptor(BaseDescriptor):
and in
class InputOutputMapList(BaseDescriptor):

in entities.py

"""
