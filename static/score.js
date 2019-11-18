document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // Let server know which room (teacher username) the student is trying to join
  socket.on('connect', function() {
    socket.emit('join', {room: localStorage.getItem("room_student_is_in")});
  });

  // The flask socket.io room name is the teacher name
  // room_name = document.querySelector('#teacher_username').innerHTML;

  console.log("AM I HERE?");

  socket.on('game over', function() {
    localStorage.clear();
    document.location.replace("/end");
  });

});
