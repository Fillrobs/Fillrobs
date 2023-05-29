# VMWare

CloudBolt's integration with VMWare vCenter (on-premise).

## VMWare APIs

VMWare supplies multiple APIs for integrations.
We currently utilize the REST endpoints and the [pyVmomi](https://vmware.github.io/pyvmomi/) (pie-vee-moh-mee) library.

There is also an open source Python sdk; the [Vsphere Automation SDK Python](https://code.vmware.com/web/sdk/7.0/vsphere-automation-python)
which we do not have installed, that mainly wraps around the REST API's functionality.

### pyVmomi

[wiki](https://github.com/vmware/pyvmomi/wiki).
[samples](https://github.com/vmware/pyvmomi/tree/master/sample)

Our internal wrapper of this library can be found in [src/resourcehandlers/vmware/pyvmomi_wrapper.py](pyvmomi_wrapper.py)

### REST

[docs](https://vdc-download.vmware.com/vmwb-repository/dcr-public/423e512d-dda1-496f-9de3-851c28ca0814/0e3f6e0d-8d05-4f0c-887b-3d75d981bae5/VMware-vSphere-Automation-SDK-REST-6.7.0/docs/apidocs/index.html),
[samples](https://code.vmware.com/samples?categories=Sample&keywords=&tags=Python&groups=&filters=&sort=dateDesc&page=)

Our internal wrapper of the REST endpoints can be found in [src/resourcehandlers/vmware/vapi_wrapper.py](vapi_wrapper.py)

## Architecture

### Components
Like all other resource technology wrappers in CloudBolt, we have a basic
`TechnologyWrapper` class defined in [`src/resourcehandlers/vmware/vmware_41.py`](https://github.com/CloudBoltSoftware/cloudbolt/blob/develop/src/resourcehandlers/vmware/vmware_41.py), which serves as the main interface bridging our internal
wrapping of the external VMWare APIs with the internal ResourceHandler framework.

However, because we wrap not just one, but two different APIs, the TechnologyWrapper
serves as a layer on top of the two API-specific wrappers;
which are found in separate files; `pyvmomi_wrapper.py` and `vapi_wrapper.py`.
Some actions and functionalities require use of both APIs. We have the `tools/interactive_wrapper.py`
file to encapsulate those multi-API approaches.

Note that inside of this vmware app, we also have the `nsx` app, which encapsulates our
integration with the vmware nsx features, having its own wrapper as well.

It might be helpful to think of these in layers, like so:

```text
                                                              +--------+
                                                              |        |
                                                              | tools/ |
                                     +--------------------+   |        |
                                     |                    |   +---^--^-+
                               +---->+ pyvmomi_wrapper.py |       |  |
+-----------+   +--------------+     |                    +-------+  |
|           |   |              |     +--------------------+          |
| models.py +-->+ vmware_41.py |                                     |
|           |   |              |     +--------------------+          |
+-----------+   +--------------+     |                    |          |
                               |     | vapi_wrapper.py    +----------+
                               +---->+                    |
                                     +--------------------+
```
