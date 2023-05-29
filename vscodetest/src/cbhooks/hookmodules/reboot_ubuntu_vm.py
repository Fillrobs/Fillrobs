import time

from utilities.exceptions import CloudBoltException
import resourcehandlers.vmware.pyvmomi_wrapper as pyvmomi_wrapper

"""
Waits for a given time, then reboots the vm.

For use at the post_networkconfig hookpoint when provisioning Ubuntu 14
servers. The OS does not recognize the new hostname set by VMware tools until
after the vm has been rebooted. We wait for a given amount of time so that
VMware tools can change the necessary files in the OS, then initiate reboot.

Skip the hook if the server cannot be rebooted (ex. some rh's do not support
reboot) or it is not an Ubuntu server.
"""


def run(job, logger=None):
    # since this is prov job, there will be only one server
    svr = job.server_set.last()
    if not svr.can_reboot() or not svr.os_family or not svr.os_family.name == "Ubuntu":
        job.set_progress("Reboot of server skipped")
        return "", "", ""

    wait_for_readiness(svr, job, logger)

    job.set_progress("Initiating server reboot")
    success = svr.reboot()

    # can't be guaranteed that 'success' is True/FalseWithMessage obj
    reboot_msg = getattr(success, "msg", None)
    if not reboot_msg:
        reboot_msg = (
            "Reboot of server {} returned status {}. "
            "See job log for more details.".format(
                svr.hostname, "SUCCESS" if success else "FAILURE"
            )
        )

    logger.debug("Reboot returned status: {}".format(success))

    wait_for_reboot_to_begin(svr, job, logger)

    status = ""
    output = ""
    error = ""
    if not success:
        status = "FAILURE"
        error = reboot_msg

    return status, output, error


def wait_for_readiness(server, job, logger):
    """
    Wait for the server to be ready to be rebooted.

    In order to reboot a vm, the os must be completely up. With non-vmware
    servers, there is not yet a way to do this. The VMware resource handler
    does provide a method for this though.
    """
    rh = server.resource_handler.cast()
    is_vmware = rh.type_slug == "vmware"
    wait_time = 240 if is_vmware else 90

    job.set_progress(
        "Waiting up to {} seconds before rebooting server".format(wait_time)
    )

    if is_vmware:
        wait_for_vmware_readiness(server, rh, logger, timeout=wait_time)
    else:
        time.sleep(wait_time)


def wait_for_reboot_to_begin(server, job, logger, timeout=120):
    """
    Wait for VMware Tools to no longer recognize the server IP

    After a server has been rebooted, it takes vmware tools several seconds to
    no longer recognize the server ip.

    This method is required for Ubuntu v13 and earlier.  In these versions of
    ubuntu, vmware correctly recognizes the server's ip and hostname before we
    even call this hook to reboot the server. After this hook, our task is to
    wait for the OS to be fully booted and customized.  However, since the ip
    and hostname have been cached, without this wait, the hook would
    incorrectly assume the OS has been fully booted. The solution is to make
    sure that vmware tools recognizes the reboot before continuing.

    This method is not necessary for Ubuntu v14. VMware gives us no way to
    determine the version of this Ubuntu server, so we assume that we must
    always perform this wait.

    Order of operations during prov:

        Prov job
            poweron

        Reboot ubuntu hook
            wait for ip to be set      <-- vmware caches both ip and hostname
            reboot                     <-- vmware could still recognize
                                           ip/hostname as being set
            wait for ip to not be set  <-- without this the prov job would
                                           immediately recognize the
                                           ip/hostname as being set

        Prov job
            wait for ip and hostname to be set
    """
    rh = server.resource_handler
    if not rh.type_slug == "vmware":
        logger.info("Reboot initialized for this non-VMware server")
        return

    logger.info(
        "Waiting for OS reboot to begin. Waiting until VMware no "
        "longer reports an IP for this server."
    )

    vm = get_pyvmomi_vm(server, rh)
    completed = pyvmomi_wrapper.wait_for_ip_to_not_be_set(
        vm, time.time(), timeout  # start_time,
    )  # timeout_seconds,

    if not completed:
        raise CloudBoltException(completed.msg)


def wait_for_vmware_readiness(server, rh, logger, timeout=240):
    """
    Wait for a vmware server to be ready by waiting until it has been given an
    ip.
    """
    vm = get_pyvmomi_vm(server, rh)
    completed = pyvmomi_wrapper.wait_for_ip_to_be_set(
        vm, time.time(), timeout  # start_time,
    )  # timeout_seconds,

    if not completed:
        raise CloudBoltException(completed.msg)


def get_pyvmomi_vm(server, rh):
    si = pyvmomi_wrapper.get_connection(
        rh.ip, rh.port, rh.serviceaccount, rh.servicepasswd
    )
    vm = pyvmomi_wrapper.get_vm(si, server)
    return vm
