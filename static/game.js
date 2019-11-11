document.addEventListener('DOMContentLoaded', () => {

  room_name = document.querySelector('#room_name').innerHTML;

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('end game', function() {
    document.location.replace("/end");
  });

  // Let server know which room (teacher username) the student is trying to join
  socket.on('connect', function() {
    socket.emit('join', {room: room_name});
  });


  // Listen for question sent from server
  socket.on('question', data => {

    document.getElementById('game_name').innerHTML = data.game;

    // Create a form based on the question received by the server
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
        "<input type='hidden' name='question_number' value='" + data.question_id + "'>" +
        "<input type='hidden' name='game_name' value='" + data.game + "'>" +
        "<br>" +
        "<button type='submit' class='btn btn-primary btn-block'>Submit Answer</button>"
      "</form>";

    });

  socket.on('end game', function() {
    document.location.replace("/end");
  });

});
