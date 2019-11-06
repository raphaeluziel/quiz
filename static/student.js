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

});
