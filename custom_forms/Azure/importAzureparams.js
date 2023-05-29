function importAzureparams(CI_Azure_environment_id) {
  // Your event listener code here

  console.log("Button clicked" + CI_Azure_environment_id);
  importAzureparamsDiv = document.getElementById("importAzureparams_res");
  while (importAzureparamsDiv.classList.length > 0) {
    importAzureparamsDiv.classList.remove(importAzureparamsDiv.classList.item(0));
  }
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-x460h61k/run/?CI_Azure_environment_id=" +
    CI_Azure_environment_id +
    "&token=vv7Srl3aLl8GJF4LwWJRXez3rrGh5dQNjTEbuGP4o5E";
  $.ajax({
    url: getval_url,
    type: "GET",
    beforeSend: function () {
      importAzureparamsDiv = document.getElementById("importAzureparams_res");
      importAzureparamsDiv.classList.add("alert", "alert-info");
      importAzureparamsDiv.innerHTML = "...loading";
    },
    complete: function () {
      importAzureparamsDiv = document.getElementById("importAzureparams_res");
      importAzureparamsDiv.classList.remove("alert", "alert-info");
      importAzureparamsDiv.classList.add("alert", "alert-success");
      importAzureparamsDiv.innerHTML = "Azure Params imported Successfully";
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
