document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // The flask socket.io room name is the teacher name
  room_name = document.querySelector('#teacher_username').innerHTML;
  localStorage.setItem("room_teacher_is_in", room_name);

  // Let teacher know which questions teacher has already sent out
  // Teacher may choose to send question out again
  questions_sent = []
  localStorage.setItem("questions_sent", JSON.stringify(questions_sent));

  // Teacher joins the room upon connecting to the socket
  socket.on('connect', function() {
    socket.emit('join', {room: room_name});
  });

  // Get number of questions in game by searching the HTML:
  num_questions = document.getElementById("upcoming_questions").getElementsByTagName("li").length;

  // Listen for any clicks
  document.addEventListener("click", function(e){

    // Get the id of the element that is clicked
    question_id = e.target.id;

    // Extract the number part of the question_id, and make it a number
    question_id_number = parseInt(question_id.replace("question", ""), 10);
    console.log("original question id numbner", question_id_number);

    // Test to see if the id of the element cicked was a question using a regex
    if (/^question/.test(question_id)){

      // Collapse all questions
      var question_element = document.getElementById("upcoming_questions").getElementsByTagName("li");
      for (i = 0; i < num_questions; i++) {
        var divElement = question_element[i].childNodes[1];
        divElement.className = "game-questions";
      };

      // Change styling of active questionto see the whole question
      document.getElementById(question_id).className = "show-game-question";

      // Data to send to student
      data = {
        "question_id": question_id_number,
        "game_name": document.querySelector("#game_name").innerHTML,
        "teacher_id": document.querySelector("#teacher_id").innerHTML,
      };

      document.getElementById("send_question" + question_id_number).onclick = () => {
        questions_sent = JSON.parse(localStorage.getItem("questions_sent"));
        question_id_number_as_string = question_id_number;
        console.log("questions_sent", questions_sent);
        console.log("question_id_as_string", question_id_number_as_string);
        if (!(question_id_number_as_string in questions_sent)) {
          questions_sent.push(question_id_number_as_string);
          localStorage.setItem("questions_sent", JSON.stringify(questions_sent));
        }
        else {
          console.log("elsing");
          document.getElementById("has_question_been_sent").innerHTML = "Question has been sent already, but you may send again.";
        }
        // Send question to the server
        socket.emit('play game', data);
      };

    };
  });


  // Tell server to sort and calculate student results
  document.getElementById("calculate_results").onclick = () => {
    socket.emit('calculate results', {room: room_name});
  };


  // Listen to server for signal that results are ready to display
  socket.on('show results', function() {
    document.location.replace("/results");
  });

});
