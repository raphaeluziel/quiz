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



    });

});
