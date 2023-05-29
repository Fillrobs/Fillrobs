from utilities.logger import ThreadLogger
import requests
from datetime import timedelta
import datetime
from infrastructure.models import Server

logger = ThreadLogger(__name__)


class TechnologyWrapper(object):
    def __init__(
        self, resource_handler, host, resource_handler_svr_id, protocol="http"
    ):
        """
        Initialising the TechnologyWrapper to get performance metrics using gnocchi service
        """
        port = self._get_service_port(resource_handler, "metric")
        self.base_url = f"{protocol}://{host}:{port}/v1/"
        self.resource_handler_svr_id = resource_handler_svr_id
        self.resource_handler = resource_handler

    def _get_performance_metric_ids(self):
        """
        This function will return the metrics ids for each type memory, cpu, disk and network
        """
        response_data = {}
        # response_data["memory_usage"] = self._get_metric_ids("memory", "").get(
        #    "memory_usage"
        # )
        response_data["memory_usage"] = 1
        # response_data["cpu_usage"] = self._get_metric_ids("cpu", "").get("cpu_usage")
        response_data["cpu_usage"] = 2
        # response_data["disk_usage"] = self._get_metric_ids("disk", "instance_disk").get(
        #    "disk_usage"
        # )
        response_data["disk_usage"] = 3
        # response_data["disk_write_usage"] = self._get_metric_ids(
        #    "disk", "instance_disk"
        # ).get("disk_write_usage")
        response_data["disk_write_usage"] = 4
        # response_data["network_usage"] = self._get_metric_ids(
        #    "network", "instance_network_interface"
        # ).get("network_usage")
        response_data["network_usage"] = 5
        # response_data["network_outgoing_usage"] = self._get_metric_ids(
        #    "network", "instance_network_interface"
        # ).get("network_outgoing_usage")
        response_data["network_outgoing_usage"] = 6
        return response_data

    def _get_metric_ids(self, metric_type, param=None):
        """
        This function call API to fetch the metrics ids for each type disk, network, memory and cpu


        headers = {
            "X-auth-token": "",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.resource_handler._check_token_validation():
            headers["X-auth-token"] = self.resource_handler.cast().api_auth_token
        else:
            token = self.resource_handler._generate_token()
            headers["X-auth-token"] = token
        if metric_type == "disk" or metric_type == "network":
            url = f"{self.base_url}search/resource/{param}"
            payload = {"=": {"instance_id": f"{self.resource_handler_svr_id}"}}
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                verify=self.resource_handler.enable_ssl_verification,
            )
        else:
            url = f"{self.base_url}resource/instance/{self.resource_handler_svr_id}"
            response = requests.get(
                url,
                headers=headers,
                verify=self.resource_handler.enable_ssl_verification,
            )
        if response.status_code == 200:
            json_response = response.json()
            metrics = (
                json_response["metrics"]
                if type(json_response).__name__ == "dict"
                else json_response[0]["metrics"]
                if type(json_response).__name__ == "list" and len(json_response) > 0
                else {}
            )
            response_data = {}
            response_data["memory_usage"] = metrics.get("memory.usage")
            response_data["cpu_usage"] = metrics.get("cpu")
            response_data["disk_usage"] = metrics.get("disk.device.read.bytes")
            response_data["disk_write_usage"] = metrics.get("disk.device.write.bytes")
            response_data["network_usage"] = metrics.get("network.incoming.bytes")
            response_data["network_outgoing_usage"] = metrics.get(
                "network.outgoing.bytes"
            )
            return response_data
        elif response.status_code == 404:
            raise Exception("Telemetry Services not configured")
        else:
            raise Exception("Can't fetch Metrics")
        """
        rh = self.resource_handler
        rhc = rh.cast()
        serversList = []
        for server in rhc.server_set.all():
            server = Server.objects.get(id=server.id)
            srv_stats = server.get_resource_history(
                datetime.datetime(2023, 5, 1), datetime.datetime(2023, 5, 9)
            )
            os_build_name = ""
            if getattr(server, "os_build", None):
                os_build_name = server.os_build.name
            cpu_hrs_on = 0
            if getattr(srv_stats, "cpu_hrs_on", None):
                cpu_hrs_on = srv_stats["cpu_hrs_on"]
            serversList.append(
                {
                    "id": server.id,
                    "name": server.hostname,
                    "cpu": server.cpu_cnt,
                    "memory": server.mem_size,
                    "disk": server.disk_size,
                    "os": os_build_name,
                    "uptime_in_days": round(cpu_hrs_on / 86400, 2),
                    "uptime_in_hours": round(cpu_hrs_on / 3600, 2),
                    "uptime_in_minutes": round(cpu_hrs_on / 60, 2),
                }
            )
        return serversList

    def collect_vm_performance(
        self, metric, metric_ids, start_date=None, end_date=None
    ):
        """
        This function returns performance metrics for each type memory, cpu, disk and network
        """
        try:
            if metric_ids:
                usage_for_vms = []
                memory_metrics = self.collect_vm_usage(
                    metric,
                    metric_ids.get("memory_usage"),
                    "memory",
                    start_date,
                    end_date,
                )
                cpu_metrics = self.collect_vm_usage(
                    metric, metric_ids.get("cpu_usage"), "cpu", start_date, end_date
                )
                network_metrics = self.collect_vm_usage(
                    metric,
                    metric_ids.get("network_usage"),
                    "network",
                    start_date,
                    end_date,
                )
                network_outgoing_metrics = self.collect_vm_usage(
                    metric,
                    metric_ids.get("network_outgoing_usage"),
                    "network",
                    start_date,
                    end_date,
                )
                disk_write_metrics = self.collect_vm_usage(
                    metric,
                    metric_ids.get("disk_write_usage"),
                    "disk",
                    start_date,
                    end_date,
                )
                disk_metrics = self.collect_vm_usage(
                    metric, metric_ids.get("disk_usage"), "disk", start_date, end_date
                )
                json_data = {}
                json_data["mem_usage_average"] = memory_metrics.get("average")
                json_data["mem_usage_values"] = memory_metrics.get("values")
                json_data["cpu_usage_average"] = cpu_metrics.get("average")
                json_data["cpu_usage_values"] = cpu_metrics.get("values")
                json_data["disk_write_usage_latest"] = disk_write_metrics.get("average")
                json_data["disk_write_usage_values"] = disk_write_metrics.get("values")
                json_data["disk_usage_latest"] = disk_metrics.get("average")
                json_data["disk_usage_values"] = disk_metrics.get("values")
                json_data["net_usage_average"] = network_metrics.get("average")
                json_data["net_usage_values"] = network_metrics.get("values")
                json_data["net_outgoing_usage_average"] = network_outgoing_metrics.get(
                    "average"
                )
                json_data["net_outgoing_usage_values"] = network_outgoing_metrics.get(
                    "values"
                )
                usage_for_vms.append(json_data)
                return usage_for_vms
            else:
                raise Exception("Metrics Not found")
        except Exception as e:
            raise Exception(f"Exception: {e.args[0]}")

    def collect_vm_usage(
        self, metric, metric_id, metric_type, start_date=None, end_date=None
    ):
        """
        This function call API to fetch the performance metrics for each type memory, cpu, disk and network
        """
        url = f"{self.base_url}metric/{metric_id}/measures"
        responsejson = {}
        if metric:
            if start_date and end_date:
                params = f"?start={start_date}&stop={end_date}"
            else:
                params_values = self._get_start_stop_time_value(metric)
                params = f'?start={params_values.get("start")}&stop={params_values.get("stop")}'
            url += params
            response_data = {}
            if metric_type == "network":
                # The response data is bytes/5min converting it to bytes/sec and then kb/sec
                metrics = [round(data[-1] / 300, 2) for data in responsejson]
            elif metric_type == "cpu":
                # Changing VIRT to CPU%
                metrics = [data[-1] for data in responsejson]
                metrics = self._get_cpu_utilisation(metrics)
            elif metric_type == "disk":
                metrics = [round(data[-1] / 1000, 2) for data in responsejson]
            else:
                metrics = [round(data[-1], 2) for data in responsejson]
            metrics = (
                metrics[0::12]
                if metric == "last_week"
                else metrics[0::24]
                if metric == "last_month"
                else metrics
            )
            response_data["average"] = (
                round(sum(metrics) / len(metrics), 2) if len(metrics) > 0 else 0.0
            )
            response_data["values"] = metrics
            return response_data

        """
        headers = {
            "X-auth-token": "",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.resource_handler._check_token_validation():
            headers["X-auth-token"] = self.resource_handler.cast().api_auth_token
        else:
            token = self.resource_handler._generate_token()
            headers["X-auth-token"] = token
        response = requests.get(
            url, headers=headers, verify=self.resource_handler.enable_ssl_verification
        )
        if response.status_code == 200:
            response_data = {}
            if metric_type == "network":
                # The response data is bytes/5min converting it to bytes/sec and then kb/sec
                metrics = [round(data[-1] / 300, 2) for data in response.json()]
            elif metric_type == "cpu":
                # Changing VIRT to CPU%
                metrics = [data[-1] for data in response.json()]
                metrics = self._get_cpu_utilisation(metrics)
            elif metric_type == "disk":
                metrics = [round(data[-1] / 1000, 2) for data in response.json()]
            else:
                metrics = [round(data[-1], 2) for data in response.json()]
            metrics = (
                metrics[0::12]
                if metric == "last_week"
                else metrics[0::24]
                if metric == "last_month"
                else metrics
            )
            response_data["average"] = (
                round(sum(metrics) / len(metrics), 2) if len(metrics) > 0 else 0.0
            )
            response_data["values"] = metrics
            return response_data
            
        
        else:
            raise Exception(f"{response.status_code} Something went wrong")
        """

    def _get_start_stop_time_value(self, metric):
        """
        This function will return the start and stop time for API params
        """
        now_datetime = datetime.now()
        if metric == "last_hour":
            start_datetime = now_datetime - timedelta(hours=1)
            start = datetime.strftime(start_datetime, "%Y-%m-%dT%H:%M")
            stop = datetime.strftime(now_datetime, "%Y-%m-%dT%H:%M")
        elif metric == "last_day":
            start_datetime = now_datetime - timedelta(hours=24)
            start = datetime.strftime(start_datetime, "%Y-%m-%dT%H:%M")
            stop = datetime.strftime(now_datetime, "%Y-%m-%dT%H:%M")
        elif metric == "last_week":
            start_datetime = now_datetime - timedelta(days=7)
            start = datetime.strftime(start_datetime, "%Y-%m-%dT%H:%M")
            stop = datetime.strftime(now_datetime, "%Y-%m-%dT%H:%M")
        elif metric == "last_month":
            start_datetime = now_datetime - timedelta(days=30)
            start = datetime.strftime(start_datetime, "%Y-%m-%dT%H:%M")
            stop = datetime.strftime(now_datetime, "%Y-%m-%dT%H:%M")
        return {"start": start, "stop": stop}

    def _get_cpu_utilisation(self, metrics):
        """
        This function will calculate the cpu utilisation, converting nanoseconds to cpu %
        """
        cpu_utilisation = []
        for i in range(0, len(metrics) - 1):
            cpu = (((metrics[i + 1] - metrics[i]) / 300) / 1000000000) * 100
            cpu = round(cpu * 100, 2)
            cpu_utilisation.append(cpu)
        return cpu_utilisation

    def _get_service_port(self, resource_handler, service):
        """
        auth_version = "v3" if "A3" in resource_handler.auth_policy else "v2.0"
        compute_version = "2" if "C2" in resource_handler.auth_policy else "3"
        conn = connection.Connection(
            auth=dict(
                auth_url=f"{resource_handler.protocol}://{resource_handler.ip}:{resource_handler.port}/{auth_version}",
                username=resource_handler.serviceaccount,
                password=resource_handler.servicepasswd,
                project_id=resource_handler.project_id,
                user_domain_name=resource_handler.domain,
            ),
            verify=resource_handler.get_ssl_verification(),
            compute_api_version={compute_version},
        )
        url = conn.endpoint_for(service_type=service)
        port = url.split(":")[-1]

        """
        rhc = resource_handler.cast()
        port = rhc.port

        return port
