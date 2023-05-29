function importAzurenetworks(CI_Azure_environment_id) {
  // Your event listener code here

  console.log("Button clicked");
  importAzurenetworksDiv = document.getElementById("importAzurenetworks_res");
  while (importAzurenetworksDiv.classList.length > 0) {
    importAzurenetworksDiv.classList.remove(
      importAzurenetworksDiv.classList.item(0)
    );
  }
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-xu47t9oo/run/?CI_Azure_environment_id=" +
    CI_Azure_environment_id +
    "&token=hyd7axxJDlzoNSizmeHOUfPJUwDZ6Ro4x3un3YOodrA";
  $.ajax({
    url: getval_url,
    type: "GET",
    beforeSend: function () {
      importAzurenetworksDiv = document.getElementById(
        "importAzurenetworks_res"
      );
      importAzurenetworksDiv.classList.add("alert", "alert-info");
      importAzurenetworksDiv.innerHTML = "...loading";
    },
    complete: function () {
      importAzurenetworksDiv = document.getElementById(
        "importAzurenetworks_res"
      );
      importAzurenetworksDiv.classList.remove("alert", "alert-info");
      importAzurenetworksDiv.classList.add("alert", "alert-success");
      importAzurenetworksDiv.innerHTML = "Azure Params imported Successfully";
    },
    success: function (data) {
      console.log("data=" + data);
      //self.popAzuredata.bind({ survey: survey })(data[1]);
    },
    error: function (data) {
      console.log("fail");
      console.log(data);
    },
  });
}
