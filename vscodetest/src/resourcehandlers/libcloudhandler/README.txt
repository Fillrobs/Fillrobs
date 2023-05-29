Libcloud is an abstract Resource Handler, others (like GCE and OpenStack)
subclass it.

Why does 'libcloudhandler' have 'handler' is in its name (unlike the other RHs)?
To give it a unique name.  "libcloud" is the name of a 3rd party module we
import, and we did not want to overload that name.
