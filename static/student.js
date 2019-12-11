document.addEventListener('DOMContentLoaded', () => {

  var teacher_list = [];
  var student_list = [];

  var teacher_selected = "";
  var student_name = "";

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // Upon connecting to server get list of teachers for typeahead
  socket.on('connect', function() {
    socket.emit('request teacher list');
  });

  // Listen to server for teacher list
  socket.on('teacher list', function(data){

    teacher_list = data.teachers;

    var substringMatcher = function(strs) {
      return function findMatches(q, cb) {
        var matches, substringRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        substrRegex = new RegExp(q, 'i');

        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(strs, function(i, str) {
          if (substrRegex.test(str)) {
            matches.push(str);
          }
        });

        cb(matches);
      };
    };

    $('#teacher_search .typeahead').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    },
    {
      name: 'teachers',
      source: substringMatcher(teacher_list)
    });
  });

  document.getElementById("select_teacher").addEventListener("click", function(){

    teacher_selected = document.getElementById("teacher_selected").value

    if (teacher_list.includes(teacher_selected)){

      // Erase any previous error messages
      document.getElementById("error_message").innerHTML = "";

      // Show student name selection section
      document.getElementById("student_name").style.visibility = "visible";

      // Get a list of students associated with teacher chosen
      socket.emit('request student list', {"teacher":teacher_selected});

      // Listen for server response with student list
      socket.on('student list', function(data) {
        student_list = data.students;
      });

    }
    else{
      document.getElementById("error_message").innerHTML = "Teacher is not in our database";
    }

  });



  document.getElementById("choose_name").addEventListener("click", function(){

    student_name = document.getElementById("student_chosen_name").value;

    if (!student_list.includes(student_name)){

      // Erase any previous error messages
      document.getElementById("error_message").innerHTML = "";

      // Student can try now to join teacher's room
      localStorage.setItem("room_student_is_in", teacher_selected);

      data = {
        "room": teacher_selected,
        "student": student_name
      }
      socket.emit('join', data);
      console.log("I made it here", "/game/" + teacher_selected);
      //document.location.replace("/game/" + teacher_selected);
    }
    else{
      document.getElementById("error_message").innerHTML = "Name is already being used";
      student_name = "";
    }

  });

  // OK, all good, student proceeds to gam
  socket.on("student goes to game", function(data){
    
  });

});
