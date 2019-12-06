document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // The flask socket.io room name is the teacher name
  var room_name = localStorage.getItem("room_teacher_is_in");

  // Teacher joins the room upon connecting to the socket
  socket.on('connect', function() {
    socket.emit('join', {room: localStorage.getItem("room_teacher_is_in")});
  });

  // Send signal to server that the all questions have been sent out
  document.querySelector('#end_game').onclick = () => {
    var data = {
      "game_id": "Sending end of game signal"
    };
    // Send signal to server that game is over
    socket.emit('end game', data);
  };

  // Listen for signal that all questions have been sent and go to results
  socket.on('game over', data => {
    localStorage.removeItem("questions_sent");
    document.location.replace("/end_game_for_teacher");
  });

});
