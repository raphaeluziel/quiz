document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // The flask socket.io room name is the teacher name
  room_name = document.querySelector('#teacher_username').innerHTML;

  // Teacher joins the room upon connecting to the socket
  socket.on('connect', function() {
    socket.emit('join', {room: room_name});
  });


  var question_number = 0;
  var questionList = document.getElementById('upcoming_questions');
  var questionListItems = questionList.getElementsByTagName('li');

  //questionListItems[0].setAttribute("style", "background-color: #ecb176;");

  document.querySelector('#submit_question').onclick = () => {

    data = {
      "message": "pushing question through game_control",
      "question_number": question_number,
      "game_id": document.querySelector("#game_id").innerHTML,
      "teacher_id": document.querySelector("#teacher_id").innerHTML,
    };
    // Send question to the server
    socket.emit('play game', data);

    for (i = 0; i < questionListItems.length; i++){
      questionListItems[i].removeAttribute("style");
    }
    questionListItems[question_number].setAttribute("style", "background-color: #ffffc0;");

    question_number += 1;

  };

  //Listen for question from server to display on teacher game control page
  socket.on('question', data => {
    document.querySelector('#active-question').innerHTML =
      data.question +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(A) ' + data.choice_a +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(B) ' + data.choice_b +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(C) ' + data.choice_c +
      '<br>&nbsp;&nbsp;&nbsp;&nbsp;(D) ' + data.choice_d +
      '<br>Answer: <strong>' + data.answer + '</strong>';
    });

  socket.on('end game', data => {
    document.location.replace("/results");
  });

});
