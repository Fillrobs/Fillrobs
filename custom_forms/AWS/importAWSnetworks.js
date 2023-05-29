function importAWSnetworks(CI_aws_environment_id) {
  // Your event listener code here

  console.log("Button clicked");
  importAWSnetworksDiv = document.getElementById("importAWSnetworks_res");
  while (importAWSnetworksDiv.classList.length > 0) {
    importAWSnetworksDiv.classList.remove(
      importAWSnetworksDiv.classList.item(0)
    );
  }
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-n7jiiioy/run/?CI_aws_environment_id=" +
    CI_aws_environment_id +
    "&token=P7OEB5SbClf1qWpRMGVK0dnx6OpBflKO7n2MNscG_vg";
  $.ajax({
    url: getval_url,
    type: "GET",
    beforeSend: function () {
      importAWSnetworksDiv = document.getElementById("importAWSnetworks_res");
      importAWSnetworksDiv.classList.add("alert", "alert-info");
      importAWSnetworksDiv.innerHTML = "...loading";
    },
    complete: function () {
      importAWSnetworksDiv = document.getElementById("importAWSnetworks_res");
      importAWSnetworksDiv.classList.remove("alert", "alert-info");
      importAWSnetworksDiv.classList.add("alert", "alert-success");
      importAWSnetworksDiv.innerHTML = "AWS Params imported Successfully";
    },
    success: function (data) {
      console.log("data=" + data);
      //self.popAWSdata.bind({ survey: survey })(data[1]);
    },
    error: function (data) {
      console.log("fail");
      console.log(data);
    },
  });
}
