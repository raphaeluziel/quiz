document.addEventListener('DOMContentLoaded', () => {

  var teachers = [];

  // Get a list of teacher usernames from the database
  var teacherhttp = new XMLHttpRequest();
  teacherhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

      teachers = JSON.parse(this.responseText);

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
        source: substringMatcher(teachers)
      });

    }
  };
  teacherhttp.open("GET", "teacherAPI", true);
  teacherhttp.send();

  document.getElementById("student_joins_room").onsubmit = function(){

    // Start the socket connection
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    room_name = document.getElementById("teacher_selected").value;
    student_name = document.getElementById("student_chosen_name").value;
    localStorage.setItem("room_student_is_in", room_name);

    data = {
      "room": room_name,
      "student": student_name
    }

    // Let server know which room (teacher username) the student is trying to join
    socket.on('connect', function() {
      alert(data.student);
      socket.emit('join', data);
    });

  };

});
