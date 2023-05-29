Welcome to the Python API sample client!  These samples will work using Python
2.6 and 2.7, but can also serve as examples of how to interact with the CB API
using other languages.  In these directories you will find:

 - client.py - a thin client that can be used to make HTTPS calls to CB's
   REST-style API.  This client is used by the sample scripts.

 - samples/ - sample scripts for performing common actions in CB.  You can use
   these as examples to write your own, or call them directly to use them as a
   basic command-line interface to CloudBolt.

 - ext/ - a few third-party modules for Python that client.py and the sample
   scripts use.  Specifically:
    - argparse (https://docs.python.org/2.7/library/argparse.html) is included
      as it is not available by default with Python 2.6.
    - requests (http://docs.python-requests.org/en/latest/) is used by
      client.py and is widely accepted as the best HTTP library for Python.


For more info, see the docs
(https://your_cloudbolt_server/static/docs/HTML/cloudbolt-api-v2-0.html) and
the API browser (https://your_cloudbolt_server/api).
