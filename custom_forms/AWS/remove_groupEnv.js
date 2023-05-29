function remove_groupEnv(group_id, aws_environment_id) {
  // Your event listener code here

  console.log("Remove Group Env Button clicked");
  grp_removeResDivName = "grp_removeResDiv_" + group_id;
  grp_div_containerName = "grp_div_container_" + group_id;

  grp_removeResDiv = document.getElementById(grp_removeResDivName);
  while (grp_removeResDiv.classList.length > 0) {
    grp_removeResDiv.classList.remove(grp_removeResDiv.classList.item(0));
  }
  grp_div_container = document.getElementById(grp_div_containerName);
  while (grp_div_container.classList.length > 0) {
    grp_div_container.classList.remove(grp_div_container.classList.item(0));
  }

  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-n2t132o6/run/?group_id=" +
    group_id +
    "&EnvID=" +
    aws_environment_id +
    "&token=5KjNMDGy4jVZrEb-UDrzlkkGTbSPVqC8bnKg1KezJV8";

  $.ajax({
    url: getval_url,
    type: "GET",
    contentType: "application/json",
    beforeSend: function () {
      grp_removeResDiv = document.getElementById(grp_removeResDivName);
      grp_removeResDiv.classList.add("alert", "alert-info");
      grp_removeResDiv.innerHTML = "...loading";
    },

    success: function (data) {
      console.log("data=" + data);
      //self.popAWSdata.bind({ survey: survey })(data[1]);
      grp_div_container = document.getElementById(grp_div_containerName);

      grp_removeResDiv = document.getElementById(grp_removeResDivName);
      grp_removeResDiv.classList.remove("alert", "alert-info");
      grp_removeResDiv.classList.add("alert", "alert-success");
      grp_removeResDiv.innerHTML =
        "Group has been deleted from the Environment";
      grp_div_container.innerHTML = "Deleted";
      grp_div_container.classList.add("alert", "alert-danger");
      // update hiddenGrpDiv
      // update hiddenGrpDiv
      //hiddenGrpDiv = document.getElementById("hiddenGrpDiv");

      //hiddenGrpData = hiddenGrpDiv.innerHTML;
      grp_data_json = sessionStorage.getItem("groupData");
      try {
        var jsonData = JSON.parse(grp_data_json);
        console.log(
          "aws_environment_id=" + aws_environment_id + " group_id=" + group_id
        );
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
              present: false,
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
      //for (var i = 0; i < hiddenGrpDiv.length; i++) {
      // hiddenGrpDiv[i].parentNode.removeChild(hiddenGrpDiv[i]);
      //}
      // recreate
      //var hiddenGrpDiv = document.createElement("div");
      //hiddenGrpDiv.style.display = "none";
      //hiddenGrpDiv.id = "hiddenGrpDiv";
      //console.log("hiddenGrpDiv recreated");
      //console.log(JSON.stringify(replaceData));
      //hiddenGrpDiv.innerHTML = JSON.stringify(replaceData);
      sessionStorage.setItem("groupData", JSON.stringify(replaceData));
    },
    error: function (data) {
      console.log("fail");
      console.log(data);
    },
  });
}
