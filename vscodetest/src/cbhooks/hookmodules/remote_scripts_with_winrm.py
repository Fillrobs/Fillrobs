import winrm
from base64 import b64encode
from utilities.exceptions import CommandExecutionException
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run_script_on_target_winrm(
    ip,
    label,
    script_contents,
    args=None,
    username=None,
    password=None,
    transport=None,
    server=None,
):
    """
    Use WinRM to run a script on the target and return the output
    Do not modify the arguments, they will be passed from Cloudbolt
    """
    if args:
        raise NotImplementedError(
            "Using commandline arguments is not yet supported when "
            "running scripts with WinRM"
        )

    host = ip

    # Kerberos requires a FQDN for host and domain validation
    if server and server.supports_kerberos:
        nic = server.nics.first()
        domain = nic.network.dns_domain
        host = "{}.{}".format(server.hostname, domain)

    status_code = 0

    """
    CloudBolt supports multiple WinRM transports.
    NTLM:       Used by default
                Allows auth with local accounts and domain accounts (restricted to the host).

    CredSSP:    enabled with parameter "Supports CredSSP"
                Allows auth with domain accounts.  Addition auth on the domain provided by
                an allowed list configured on each host.

    Kerberos:   enabled with parameter "Supports Kerberos"
                Allows auth with local and domain accounts.  Full trusted access to the domain.
                Requires Kerberos to be configured on the os platform.
    """
    if transport:
        protocol = winrm.Protocol(
            endpoint="https://{}:5986/wsman".format(host),
            transport=transport,
            username=username,
            password=password,
            server_cert_validation="ignore",
            operation_timeout_sec=60,
            read_timeout_sec=90,
        )

        shell_id = protocol.open_shell()
        encoded_ps = b64encode(script_contents.encode("utf_16_le")).decode("ascii")
        command_id = protocol.run_command(
            shell_id, "powershell -encodedcommand {0}".format(encoded_ps)
        )
        std_out, std_err, status_code = protocol.get_command_output(
            shell_id, command_id
        )
        protocol.cleanup_command(shell_id, command_id)
        protocol.close_shell(shell_id)

    else:
        session = winrm.Session(
            ip,
            auth=(username, password),
            transport="plaintext",
            operation_timeout_sec=60,
            read_timeout_sec=90,
            server_cert_validation="ignore",
        )
        encoded_ps = b64encode(script_contents.encode("utf_16_le")).decode("ascii")
        rs = session.run_cmd("powershell -encodedcommand {0}".format(encoded_ps))
        try:
            std_out, std_err, status_code = (
                rs.std_out.decode("utf_8"),
                rs.std_err.decode("utf_8"),
                rs.status_code,
            )
        except UnicodeDecodeError as e:
            logger.debug("Error decoding WinRM response to utf-8: {}".format(e))
            std_out, std_err, status_code = rs.std_out, rs.std_err, rs.status_code

    if status_code != 0:
        logger.info("Command returned\nstdout: {}\nstderr: {}".format(std_out, std_err))
        raise CommandExecutionException(std_err, status_code, "", std_err)

    return std_out
