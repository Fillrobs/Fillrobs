function popAWSdata(EnvID) {
  var survey = this.survey;
  //console.log("survey(a)=" + survey);
  if (survey === undefined) {
    var survey = Survey.SurveyWindow.surveyInstances[0].survey;

    //console.log("survey(b)=" + survey);
  }

  var EnvID = sessionStorage.getItem("EnvID");
  //console.log("got EnvID=" + EnvID);

  survey.onCurrentPageChanged.add(function (sender, options) {
    if (options.newCurrentPage.name === "AWS Environment Groups") {
      // Run your function here

      //process_groupLink();
      if (EnvID !== null) {
        console.log("My page is in view for " + EnvID);
        var html = "";
        var targetNode = document.body;
        var config = { attributes: true, childList: true, subtree: true };
        var callback = function (mutationsList, observer) {
          for (var mutation of mutationsList) {
            if (mutation.type === "childList") {
              for (var node of mutation.addedNodes) {
                // Check if the added node is an envGroupData_ div
                if (
                  node.nodeType === 1 &&
                  node.id.startsWith("envGroupData_")
                ) {
                  // Extract the number from the div id
                  var id = parseInt(node.id.substring("envGroupData_".length));

                  //hiddenGrpDiv = document.getElementById("hiddenGrpDiv");
                  //grp_data_json = hiddenGrpDiv.innerHTML;
                  grp_data_json = sessionStorage.getItem("groupData");
                  try {
                    var jsonData = JSON.parse(grp_data_json);
                    var jsonDatacount = Object.keys(jsonData).length;

                    jsonData.forEach(function (item) {
                      var id = item.id;
                      var name = item.name;

                      var present = item.present;
                      var EnvID = item.EnvID;
                      if (present == true) {
                        // Build the HTML for the div
                        html +=
                          '<div id="grp_div_container_' +
                          id +
                          '"><a href="/groups/' +
                          id +
                          '/" target="_blank">' +
                          name +
                          '</a>&nbsp;<a href="#" onclick="remove_groupEnv(' +
                          id +
                          ", " +
                          EnvID +
                          ');" class="btn btn-default">X</a></div><div id="grp_removeResDiv_' +
                          id +
                          '" style="display:inline-block;"></div>';
                      }
                    });
                  } catch {
                    html =
                      '<span class="alert alert-danger">No Groups found</span>';
                  }
                  // Set the HTML for the div
                  node.innerHTML = html;

                  html = "";
                }
              }
            }
          }
        };

        // Create a new observer object
        var observer = new MutationObserver(callback);

        // Start observing the target node for configured mutations
        observer.observe(targetNode, config);
        // end of if current page is aws_environment groups
      }
    } else if (options.newCurrentPage.name === "Add a Group") {
      console.log("My page is in view Add a Group ");

      var html = "";
      var targetNode = document.body;
      var config = { attributes: true, childList: true, subtree: true };
      var callback = function (mutationsList, observer) {
        for (var mutation of mutationsList) {
          if (mutation.type === "childList") {
            for (var node of mutation.addedNodes) {
              // Check if the added node is an addEnvGroupForm div
              if (
                node.nodeType === 1 &&
                node.id.startsWith("addEnvGroupForm")
              ) {
                addEnvGroupForm = document.getElementById("addEnvGroupForm");
                var add_grpEnv_html = "";

                dropdown_html =
                  '<select id="add_group" name="add_group" class="selectize-input items required has-options full has-items">';

                //grp_data_json = hiddenGrpDiv.innerHTML;
                grp_data_json = sessionStorage.getItem("groupData");
                try {
                  var jsonData = JSON.parse(grp_data_json);
                  // console.log("jsonData=" + JSON.stringify(jsonData));
                  var jsonDatacount = Object.keys(jsonData).length;

                  jsonData.forEach(function (item) {
                    var id = item.id;
                    var name = item.name;

                    var present = item.present;
                    var EnvID = item.EnvID;
                    if (present == false) {
                      // Build the HTML for the dropdown
                      dropdown_html +=
                        '<option value="' + id + '">' + name + "</option>";
                    }
                  });
                  add_grpEnv_html =
                    '<div id="custom-order-form-wrap"><form><div class="form-group"><label for="add_group" class="requiredField col-lg-9 control-label">Choose a Group to add to this Environment</label></div><div class="col-lg-9 order-form__section">' +
                    dropdown_html;
                  add_grpEnv_html +=
                    '</select></div><div><a href="#" onclick="addGrouptoEnv();" class="btn btn-primary">Add</button></form></div>';
                } catch {
                  add_grpEnv_html =
                    '<div id="custom-order-form-wrap"><div class="form-group"><span class="alert alert-danger">No Groups found</span></div></div>';
                }
                // Set the HTML for the div
                addEnvGroupForm.innerHTML = add_grpEnv_html;

                add_grpEnv_html = "";
              }
            }
          }
        }
      };
      // Create a new observer object
      var observer = new MutationObserver(callback);

      // Start observing the target node for configured mutations
      observer.observe(targetNode, config);
      // end of if current page is Add a group
    }
  });

  try {
    CI_aws_environment_id = survey.getValue("CI_aws_environment_id");
    //console.log("CI_aws_environment_id(a)=" + CI_aws_environment_id);
  } catch {
    CI_aws_environment_id = EnvID;
  }

  //var hiddenGrpDiv = document.createElement("div");
  //hiddenGrpDiv.style.display = "none";
  //hiddenGrpDiv.id = "hiddenGrpDiv";
  //console.log("hiddenGrpDiv created");

  //console.log("CI_aws_environment_id(b)=" + CI_aws_environment_id);
  getval_url =
    "http://localhost:8001/api/v3/cmp/inboundWebHooks/IWH-jwe1bp2i/run/?CI_aws_environment_id=" +
    CI_aws_environment_id +
    "&token=KugXTaLLTS0EjhREzpq4G2hJaMOx1xhhRzVcw_ZXDXI";
  $.ajax({
    url: getval_url,
    type: "GET",
    success: function (data) {
      //console.log(data);
      survey.setValue("CI_awsEnvId", data[0]["awsEnvId"]);
      survey.setValue("CI_awsEnvName", data[0]["awsEnvName"]);
      survey.setValue("CI_awsAccessKey", data[0]["awsAccessKey"]);
      survey.setValue("CI_rhName", data[0]["rhName"]);
      survey.setValue("CI_awsAccountId", data[0]["awsAccountId"]);
      // AWS Parameters
      var fieldArray = [
        "zonesData",
        "elasticIpData",
        "awsHostData",
        "awsHostGroupData",
        "deleteEbsVolTermData",
        "ebsVolumeTypeData",
        "instanceTypeData",
        "iopsData",
        "keyNameData",
        "secGroupData",
        "envGroupData",
        "envNetworkData",
        "envOSBuildData",
        "envParamsData",
      ];

      group_data = data[0][fieldArray[10]];
      group_data_len = group_data.length;
      //console.log("group_data_len: ", group_data_len);
      if (group_data_len > 0) {
        var dataArr = [];
        for (g = 0; g < group_data_len; g++) {
          var dataObj = {
            id: group_data[g]["id"],
            name: group_data[g]["name"],
            present: group_data[g]["present"],
            EnvID: data[0]["awsEnvId"],
          };
          dataArr.push(dataObj);
          sessionStorage.setItem("EnvID", data[0]["awsEnvId"]);
          console.log("set EnvID=" + data[0]["awsEnvId"]);
        }
        var jsonData = JSON.stringify(dataArr);
        sessionStorage.setItem("groupData", jsonData);

        //hiddenGrpDiv.innerHTML = jsonData;
      } else {
        sessionStorage.setItem(
          "groupData",
          '<span class="alert alert-danger">No Groups found</span>'
        );
        //hiddenGrpDiv.innerHTML =
        //  '<span class="alert alert-danger">No Groups found</span>';
      }
      //document.body.appendChild(hiddenGrpDiv);
      grpDataTest = sessionStorage.getItem("groupData");
      console.log("groupData set" + grpDataTest);

      for (var i = 0; i < fieldArray.length; i++) {
        fieldData = data[0][fieldArray[i]];
        if (typeof fieldData === "undefined") {
          //console.log(fieldArray[i] + ": undefined");
        } else {
          if (fieldData.length > 0) {
            //console.log(fieldArray[i] + " fieldData=" + fieldData);
            fieldDataCount = Object.keys(fieldData).length;
            if (fieldDataCount > 0) {
              fieldData_res = process_fieldData(
                survey,
                fieldArray[i],
                fieldDataCount,
                fieldData
              );
            }
          } else {
            //console.log(fieldData + " is Null");
          }
        }
      }
    },
    error: function (data) {
      console.log("fail");
      console.log(data);
    },
  });
}
