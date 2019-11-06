document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  var question_number = 0;
  var questionList = document.getElementById('upcoming_questions');
  var questionListItems = questionList.getElementsByTagName('li');
  questionListItems[0].setAttribute("style", "background-color: lightyellow; border: 1px solid gray; border-radius: 4px; padding: 8px;");

  socket.on('connect', () => {
    document.querySelector('#submit_message').onclick = () => {
      data = {
        "message": "pushing question through game_control",
        "question_number": question_number,
        "game_id": document.querySelector("#game_id").innerHTML,
        "teacher_id": document.querySelector("#teacher_id").innerHTML,
      };
      socket.emit('start game', data);

      for (i = 0; i < questionListItems.length; i++){
        questionListItems[i].removeAttribute("style");
      }
      questionListItems[question_number].setAttribute("style", "background-color: lightyellow; border: 1px solid gray; border-radius: 4px; padding: 8px;");

      question_number += 1;

    };
  });


  socket.on('push question', data => {
    document.querySelector('#message_received').innerHTML =
      data.question +
      '<br>(A) ' + data.choice_a +
      '<br>(B) ' + data.choice_b +
      '<br>(C) ' + data.choice_C +
      '<br>(D) ' + data.choice_d;
    });

});
