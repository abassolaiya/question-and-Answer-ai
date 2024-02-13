$(document).ready(function () {
  $("#uploadForm").submit(function (event) {
    event.preventDefault();
    var formData = new FormData(this);
    $.ajax({
      url: "/api/pdf/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        $("#pdfContent").text(response.pdf_text);
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  $("#questions").on("submit", ".questionForm", function (event) {
    event.preventDefault();
    var formData = new FormData(this);
    $.ajax({
      url: "/api/qa/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        $("#answers").append(
          "<p>Q: " + response.question + "</p><p>A: " + response.answer + "</p>"
        );
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });
});
