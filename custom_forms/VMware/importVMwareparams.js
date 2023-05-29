function importVMwareparams(CI_VMware_environment_id) {
  // Your event listener code here

  console.log("Button clicked" + CI_VMware_environment_id);
  importVMwareparamsDiv = document.getElementById("importVMwareparams_res");
  while (importVMwareparamsDiv.classList.length > 0) {
    importVMwareparamsDiv.classList.remove(
      importVMwareparamsDiv.classList.item(0)
    );
  }
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-n1s306a2/run/?CI_VMware_environment_id=" +
    CI_VMware_environment_id +
    "&token=K4P9unP4olnXEHpTXnCQ3yHa14QCeb0F7B70Co0u-io";
  $.ajax({
    url: getval_url,
    type: "GET",
    beforeSend: function () {
      importVMwareparamsDiv = document.getElementById("importVMwareparams_res");
      importVMwareparamsDiv.classList.add("alert", "alert-info");
      importVMwareparamsDiv.innerHTML = "...loading";
    },
    complete: function () {
      importVMwareparamsDiv = document.getElementById("importVMwareparams_res");
      importVMwareparamsDiv.classList.remove("alert", "alert-info");
      importVMwareparamsDiv.classList.add("alert", "alert-success");
      importVMwareparamsDiv.innerHTML = "VMware Params imported Successfully";
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
