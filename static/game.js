document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('push question', data => {

    console.log(data);

    document.querySelector('#question_received').innerHTML =
      data.question +
      "<form action='' method='post'>" +
        "<div class='form-check'>" +
          "<input class='form-check-input' type='radio' name='submitted_answer' value='A' required>" +
          "<label id='label_a' class='form-check-label'>" + data.choice_a + "</label>" +
        "</div>" +
        "<div class='form-check'>" +
          "<input class='form-check-input' type='radio' name='submitted_answer' value='B' required>" +
          "<label id='label_a' class='form-check-label'>" + data.choice_b + "</label>" +
        "</div>" +
        "<div class='form-check'>" +
          "<input class='form-check-input' type='radio' name='submitted_answer' value='C' required>" +
          "<label id='label_a' class='form-check-label'>" + data.choice_c + "</label>" +
        "</div>" +
        "<div class='form-check'>" +
          "<input class='form-check-input' type='radio' name='submitted_answer' value='D' required>" +
          "<label id='label_a' class='form-check-label'>" + data.choice_d + "</label>" +
        "</div>" +
        "<input type='hidden' name='question_number' value='1'>" +
        "<br>" +
        "<button type='submit' class='btn btn-primary'>Submit Answer</button>"
      "</form>";

    });

});
