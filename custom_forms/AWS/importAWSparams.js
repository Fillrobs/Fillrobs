function importAWSparams(CI_aws_environment_id) {
  // Your event listener code here

  console.log("Button clicked");
  importAWSparamsDiv = document.getElementById("importAWSparams_res");
  while (importAWSparamsDiv.classList.length > 0) {
    importAWSparamsDiv.classList.remove(importAWSparamsDiv.classList.item(0));
  }
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-fyzbxs7r/run/?CI_aws_environment_id=" +
    CI_aws_environment_id +
    "&token=PkKoNcr1a954wdW1o2IafFe6_bnzsixMJhb0wc_pE9E";
  $.ajax({
    url: getval_url,
    type: "GET",
    beforeSend: function () {
      importAWSparamsDiv = document.getElementById("importAWSparams_res");
      importAWSparamsDiv.classList.add("alert", "alert-info");
      importAWSparamsDiv.innerHTML = "...loading";
    },
    complete: function () {
      importAWSparamsDiv = document.getElementById("importAWSparams_res");
      importAWSparamsDiv.classList.remove("alert", "alert-info");
      importAWSparamsDiv.classList.add("alert", "alert-success");
      importAWSparamsDiv.innerHTML = "AWS Params imported Successfully";
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