function addGrouptoEnv(survey) {
  console.log("survey=" + survey);

  addEnvGroupForm_res = document.getElementById("addEnvGroupForm_res");
  while (addEnvGroupForm_res.classList.length > 0) {
    addEnvGroupForm_res.classList.remove(addEnvGroupForm_res.classList.item(0));
  }

  // hiddenGrpDiv = document.getElementById("hiddenGrpDiv");
  //var grp_data_json = hiddenGrpDiv.innerHTML;
  grp_data_json = sessionStorage.getItem("groupData");
  console.log("grp_data_json =" + grp_data_json);
  var jsonData = JSON.parse(grp_data_json);
  var jsonDatacount = Object.keys(jsonData).length;
  dropdown_html = '<select id="add_group" name="add_group">';
  jsonData.forEach(function (item) {
    aws_environment_id = item.EnvID;
    console.log("EnvID =" + aws_environment_id);
  });
  var group_selected = document.getElementById("add_group");
  console.log(
    "group_selected=" + group_selected.value + " EnvID=" + aws_environment_id
  );
  group_id = group_selected.value;

  console.log("Add Group to Env Button clicked");

  //<CloudBolt_portal_URL_not_set>/api/v3/cmp/inboundWebHooks/IWH-sjk0zsu3/run/?token=ohjkZUAUHopylpkWshhsBFVdVkO0qDMvAgnVOL0SMoI
  http: getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-sjk0zsu3/run/?group_id=" +
    group_id +
    "&EnvID=" +
    aws_environment_id +
    "&token=ohjkZUAUHopylpkWshhsBFVdVkO0qDMvAgnVOL0SMoI";

  $.ajax({
    url: getval_url,
    type: "GET",
    contentType: "application/json",
    beforeSend: function () {
      addEnvGroupForm_res = document.getElementById("addEnvGroupForm_res");
      addEnvGroupForm_res.classList.add("alert", "alert-info");
      addEnvGroupForm_res.innerHTML = "...loading";
    },

    success: function (data) {
      console.log("data=" + data);
      //self.popAWSdata.bind({ survey: survey })(data[1]);
      console.log("Added Group " + group_id + " to Env " + aws_environment_id);
      // grp_div_container = document.getElementById(grp_div_containerName);

      addEnvGroupForm_res = document.getElementById("addEnvGroupForm_res");
      addEnvGroupForm_res.classList.remove("alert", "alert-info");
      addEnvGroupForm_res.classList.add("alert", "alert-success");
      addEnvGroupForm_res.innerHTML = "Group has been added to the Environment";
      // update hiddenGrpDiv
      //hiddenGrpDiv = document.getElementById("hiddenGrpDiv");

      //hiddenGrpData = hiddenGrpDiv.innerHTML;
      try {
        var jsonData = JSON.parse(grp_data_json);
        //console.log("jsonData=" + jsonData);
        var jsonDatacount = Object.keys(jsonData).length;
        var replaceData = [];
        jsonData.forEach(function (item) {
          var id = item.id;
          var name = item.name;

          var present = item.present;
          var EnvID = item.EnvID;
          if (id == group_id && EnvID == aws_environment_id) {
            var obj = {
              id: id,
              name: name,
              present: true,
              EnvID: EnvID,
            };
            replaceData.push(obj);
          } else {
            var obj = {
              id: id,
              name: name,
              present: present,
              EnvID: EnvID,
            };
            replaceData.push(obj);
          }
        });
      } catch {
        replaceData = '<span class="alert alert-danger">No Groups found</span>';
      }
      sessionStorage.setItem("groupData", JSON.stringify(replaceData));

      //for (var i = 0; i < hiddenGrpDiv.length; i++) {
      //  hiddenGrpDiv[i].parentNode.removeChild(hiddenGrpDiv[i]);
      //}
      // recreate
      //var hiddenGrpDiv = document.createElement("div");
      //hiddenGrpDiv.style.display = "none";
      //hiddenGrpDiv.id = "hiddenGrpDiv";
      console.log("groupdata recreated with " + JSON.stringify(replaceData));

      //hiddenGrpDiv.innerHTML = JSON.stringify(replaceData);
    },
    error: function (data) {
      console.log("fail");
      console.log(data);
    },
  });
}
