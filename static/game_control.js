document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // The flask socket.io room name is the teacher name
  var room_name = document.querySelector('#teacher_username').innerHTML;
  localStorage.setItem("room_teacher_is_in", room_name);

  // Remember the questions the teacher has already sent
  var questions_sent = [];

  // Teacher joins the room upon connecting to the socket
  socket.on('connect', function() {
    socket.emit('join', {room: room_name});
  });

  // Get number of questions in game by searching the HTML:
  var num_questions = document.getElementById("upcoming_questions").getElementsByTagName("li").length;

  // Listen for any clicks anywhere on the page
  document.addEventListener("click", function(e){

    // Check using a regex if what was clicked was a question (question id's end in a number)
    if ((/\d$/).test(e.target.id)){

      // Extract number portion of element clicked id, which equals the question id
      var question_id = e.target.id.match(/\d+$/)[0];

      // Collapse all questions
      var question_element = document.getElementById("upcoming_questions").getElementsByTagName("li");
      for (var i = 0; i < num_questions; i++) {
        var divElement = question_element[i].childNodes[1];
        divElement.className = "game-questions";
      }

      // Change styling of active question to see the whole question
      document.getElementById("question" + question_id).className = "show-game-question";

      // Data to send to student
      var data = {
        "question_id": question_id,
        "game_name": document.querySelector("#game_name").innerHTML,
        "teacher_id": document.querySelector("#teacher_id").innerHTML,
      };

      // If question has been sent, let teacher know
      if (questions_sent.includes(question_id)) {
        document.getElementById("send_question" + question_id).classList.remove("btn-success");
        document.getElementById("send_question" + question_id).classList.add("btn-warning");
        document.getElementById("send_question" + question_id).innerHTML = "Resend Question";
        console.log("HELL");
      }

      // Handle send question button clicks
      document.getElementById("send_question" + question_id).onclick = () => {

        // If question has been sent, let teacher know
        if (!questions_sent.includes(question_id)) {
          questions_sent.push(question_id);
          localStorage.setItem("questions_sent", JSON.stringify(questions_sent));
        }

        // Send question to the server
        socket.emit('play game', data);
      };
    }
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
