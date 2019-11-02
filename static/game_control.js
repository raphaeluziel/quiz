document.addEventListener('DOMContentLoaded', () => {

  console.log("AAAAAAAAAAAAAAAAAAAA");

  // Start the socket connection
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


  socket.on('connect', () => {
    document.querySelector('#submit_message').onclick = () => {
      console.log("BBBBBBBBBBBBBBBBBBBBBBBBBBBB");
      data = {
        "message": "trying to send a message through a socket"
      };
      socket.emit('start game', data);
    };

    console.log("HERE")
    socket.on('send receive question', data => {
      console.log(data);
      document.querySelector('#message_received').innerHTML =
        data.question +
        '<br>(A) ' + data.choice_a +
        '<br>(B) ' + data.choice_b +
        '<br>(C) ' + data.choice_C +
        '<br>(D) ' + data.choice_d;

      document.querySelector('#question_received').innerHTML =
        data.question +
        '<br>(A) ' + data.choice_a +
        '<br>(B) ' + data.choice_b +
        '<br>(C) ' + data.choice_C +
        '<br>(D) ' + data.choice_d;

      console.log("HELLL");
      document.querySelector('#question_received').innerHTML = "HELL";
    });

  });



});
