"""
This is a working sample CloudBolt plug-in for you to start with. The run method is required,
but you can change all the code within it. See the "CloudBolt Plug-ins" section of the docs for
more info and the CloudBolt forge for more examples:
https://github.com/CloudBoltSoftware/cloudbolt-forge/tree/master/actions/cloudbolt_plugins
"""
from common.methods import set_progress
from common.methods import requests

def run(job, server=None, **kwargs):
    set_progress("This will show up in the job details page in the CB UI, and in the job log")

    # Example of how to fetch arguments passed to this plug-in ('server' will be available in
    # some cases)
	
	# quotes are important
    curl_url = "{{ curl_url }}"
    set_progress("This plug-in is running for Curl target ".format(curl_url))

    set_progress("Dictionary of keyword args passed to this plug-in: {}".format(kwargs.items()))

    r = curlurl(curl_url)
    
    if True:
        return "SUCCESS", r['message'], ""
    else:
        return "FAILURE", "Sample output message", "Sample error message, this is shown in red"
        
        
        
        
def curlurl(curl_url):
     r = requests.get(curl_url)
     data = r.json()
     
     return data