function process_fieldData(survey, fieldName, fieldDataCount, fieldData) {
  //console.log("function fieldname=CI_" + fieldName);
  var fieldDataQuestion = survey.getQuestionByName("CI_" + fieldName);
  valfieldDataQuestion = fieldDataQuestion.value;
  str_valfieldDataQuestion = JSON.stringify(fieldDataQuestion);
  //console.log("str_valfieldDataQuestion=" + str_valfieldDataQuestion);
  numrecords = str_valfieldDataQuestion.items
    ? str_valfieldDataQuestion.items.length
    : 0;

  //console.log(
  //  "fieldDataQuestion=" + str_valfieldDataQuestion + " count=" + numrecords
  //);

  newitem_arr = "";
  var predefinedAnswers = fieldDataQuestion.items || [];
  var defaultValues = [];
  //console.log("predfinedAnswers=" + JSON.stringify(predefinedAnswers));
  for (n = 0; n < fieldDataCount; n++) {
    //console.log(
    //  fieldName + "=" + fieldData[n]["id"] + " " + fieldData[n]["name"]
    //);

    var newitem_id = fieldData[n]["id"];
    if (fieldData[n]["name"] != null) {
      var newitem = fieldData[n]["name"].toString().trim();
      predefinedAnswers.push({
        value: newitem_id,
        text: newitem,
      });
      defaultValues.push(newitem_id);
      fieldDataQuestion.choices = predefinedAnswers;

      if (fieldName === "envGroupData") {
        fieldDataQuestion.onAfterRenderQuestion = function (
          question,
          htmlElement
        ) {
          var hyperlink = document.createElement("a");
          hyperlink.href = "/groups/" + newitem_id + "/";
          hyperlink.target = "_blank";
          hyperlink.innerHTML = newitem;
          htmlElement.appendChild(hyperlink);
        };
      }
    }
  }

  fieldDataQuestion.defaultValue = defaultValues;
  survey.render();
}
