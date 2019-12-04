document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // The flask socket.io room name is the teacher name
  room_name = document.querySelector('#teacher_username').innerHTML;
  localStorage.setItem("room_teacher_is_in", room_name);

  // Teacher joins the room upon connecting to the socket
  socket.on('connect', function() {
    socket.emit('join', {room: room_name});
  });

  // Listen for any clicks
  document.addEventListener("click", function(e){
    // Get the id of the element that is clicked
    question_id = e.target.id;
    // Test to see if the id of the element cicked was a question using a regex
    if (/^question/.test(question_id)){
      // Extract the number part of the question_id, and make it a number
      question_id = parseInt(question_id.replace("question", ""), 10);
      // Data to send to student
      data = {
        "question_id": question_id,
        "game_name": document.querySelector("#game_name").innerHTML,
        "teacher_id": document.querySelector("#teacher_id").innerHTML,
      };
      // Send question to the server
      socket.emit('play game', data);
    }
  });

  // Finish game and show results
  document.getElementById("show_results").onclick = () => {
    socket.emit('show results', {room: room_name});
    document.location.replace("/results");
  };

  // Listen for question from server to display on teacher game control page
  socket.on('question', data => {
    document.querySelector('#active-question').innerHTML =
      data.question +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(A) ' + data.choice_a +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(B) ' + data.choice_b +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(C) ' + data.choice_c +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(D) ' + data.choice_d +
      '<br>Answer: <strong>' + data.answer + '</strong>';
    });

});
