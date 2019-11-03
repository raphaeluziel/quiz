document.addEventListener('DOMContentLoaded', () => {

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('push question', data => {
    document.querySelector('#message_received').innerHTML =
      data.question +
      '<br>(A) ' + data.choice_a +
      '<br>(B) ' + data.choice_b +
      '<br>(C) ' + data.choice_C +
      '<br>(D) ' + data.choice_d;

      document.querySelector('#label_a').innerHTML = data.choice_a;

      var answers = document.getElementById("answers");

      var question = document.createElement("div");
      question.innerHTML = data.question;
      answers.appendChild(question);

      var label = document.createElement("label");
      var radio = document.createElement("input");

      radio.type = "radio";
      radio.name = "submitted_answer";
      radio.value = "A";

      label.appendChild(radio);

      label.appendChild(document.createTextNode(data.choice_a));

      answers.appendChild(label)


    });

});
