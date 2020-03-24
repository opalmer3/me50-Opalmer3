document.addEventListener('DOMContentLoaded', () => {
  // Connect to web socketio
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // When connected, listen for sent messages
  socket.on('connect', () => {
    document.querySelector("#myForm").addEventListener("submit", event => {
      // Reset error message
      document.querySelector("#error").innerHTML = "";

      var msg = document.querySelector("#message").value;

      // channel id saved in send button to pass to server
      var id = document.querySelector("#send").value;

      //Ensure message field not blank and emit message to app
      if (msg.length > 0){
        var name = localStorage.getItem("displayname");
        var now = Date(Date.now()).toString().slice(0,24);
        socket.emit('send', {'msg': msg, 'name': name, 'datetime': now, 'id': id});
      }

      // Prevent form submission and clear message box
      event.preventDefault();
      document.querySelector("#message").value = "";
    });

  });

  // When a message submitted show it on all users screens
  socket.on('receive', data => {
    // create div containing message
    const messageinfo = document.createElement('div');
    const message = document.createElement("p");
    const sender = document.createElement("p");
    const timedate = document.createElement("p");
    var displayname = localStorage.getItem('displayname');
    var comments = document.querySelector('#comments');

    timedate.setAttribute('class', "msgtime");
    sender.setAttribute('class', "msgsender");
    message.setAttribute('data-id', data['msgid']);
    message.setAttribute('data-sender', data['name']);

    //if message sent by user then add appropriate css classes
    if (data['name'] == displayname){
        messageinfo.setAttribute('class', "msginfo right")
        message.setAttribute('class', "msg sent");
        message.setAttribute('oncontextmenu', "return contextmenu(event);");
    }
    else{
      messageinfo.setAttribute('class', "msginfo")
      message.setAttribute('class', "msg");
    }
    sender.innerHTML = data['name'];
    message.innerHTML =  data['msg'];
    timedate.innerHTML = data['datetime'];

    // append message info and message div to comments div
    messageinfo.appendChild(sender);
    messageinfo.appendChild(message);
    messageinfo.appendChild(timedate);
    document.querySelector("#comments").appendChild(messageinfo);

    //Delete oldest messagee if more than 100 messages
    var count = document.querySelector("#comments").childElementCount;
    if (count > 100){
      document.querySelector("#comments").firstElementChild.remove();
    }

    // scroll to bottom of comments div if scroll bar already near bottom
    var height = comments.scrollHeight;
    var scrolled = comments.scrollTop;

    if (height - scrolled < 2000){
      comments.scrollTop = comments.scrollHeight;
    }

  });

  // Display error message if error in inserting message into db
  socket.on('error', data => {
    document.querySelector("#error").innerHTML = "Message could not be sent";
    });

});

// When enter pressed in textare submit message
document.addEventListener("DOMContentLoaded", () => {
  document.querySelector('#message').addEventListener('keypress', e => {
    if (e.which == 13 || e.keyCode == 13){
      e.preventDefault();
      document.querySelector('#send').click();
      document.querySelector('#message').value = "";
    }
  }) ;
});

// Iterate through messages on page and add sent/right/recalled/deleted class if message sent by user. Also set scroll position to bottom of comments div
document.addEventListener("DOMContentLoaded", () => {
  var comments = document.querySelector('#comments');
  var messages = document.querySelectorAll('.msginfo')
  var len = messages.length;
  var displayname = localStorage.getItem('displayname');

// iterate over each message
  for (var i = 0; i < len; i++){
    let sentby = messages[i].firstElementChild.innerHTML;
    let msg = messages[i].getElementsByTagName('p')[1];

    if (sentby == displayname){
      messages[i].setAttribute('class', "msginfo right");
      messages[i].getElementsByTagName('p')[1].setAttribute('class', "msg sent");
    }

    if (msg.innerHTML == 'Message recalled' || msg.innerHTML == 'Message deleted'){
      msg.setAttribute('class', "msg deleted-recalled");
    }

  }

  // set scroll position to bottom of comments div
comments.scrollTop = comments.scrollHeight;
});

// variable to store if navigation is valid
var validNavigation = false;

// If link clicked then navigation is valid
document.querySelectorAll('a').forEach(function(a){
  a.addEventListener('click', () => {
    validNavigation = true;
  });
});


// Store last viewed channel in local memory if navigation valid
window.onbeforeunload = () => {
  if (!validNavigation){
    var url = window.location.href;
    localStorage.setItem('lastviewed', url);
    return null;
  }
}

// initailise dict key: months value: datenumbers for creating date object for compariosn of time message sent to time now. see contextmenu function
var months = {};
months.Jan = 01;
months.Feb = 02;
months.Mar = 03;
months.Apr = 04;
months.May = 05;
months.Jun = 06;
months.Jul = 07;
months.Aug = 08;
months.Sep = 09;
months.Oct = 10;
months.Nov = 11;
months.Dec = 12;

//Adds 0 padding to numbers <10
function pad2(number){
  if (number < 10){
    return '0' + number;
  }
}
// Show righclick menu on right click
function contextmenu(event){
  // Get display name and message sender for comparison
  let displayname = localStorage.getItem('displayname');
  let element = event.toElement;
  let sender = element.dataset.sender;
  let id = element.dataset.id;
  let msg = element.innerHTML;
  let timesent = element.parentNode.getElementsByTagName('p')[2].textContent;

  // parse timsent string to correct format for creating new date object
  let day = timesent.slice(8,10);
  let month = pad2(months[timesent.slice(4,7)]);
  let year = timesent.slice(11,15);
  let time = timesent.slice(16,24);

  // date object of time message sent
  let dtimesent = new Date(year + '-' + month + '-' + day + 'T' + time);
  let timenow = new Date(Date.now());
  // time differnce in milliseconds between time message sent and time now
  let diff = timenow - dtimesent;

  // If displayname = sender then create the right click menu, and add event listener to the menu options
  if (sender == displayname && msg != 'Message recalled' && msg != 'Message deleted'){
    let rmenu = document.createElement('div');
    rmenu.setAttribute('class', "rmenu");

    let ul = document.createElement('ul');
    let recallli = document.createElement('li');
    recallli.setAttribute('id', "recall");
    recallli.innerHTML = "Recall";

    let deleteli = document.createElement('li');
    deleteli.setAttribute('id', "delete");
    deleteli.innerHTML = "Delete";

    rmenu.appendChild(ul);
    ul.appendChild(recallli);
    ul.appendChild(deleteli);

    document.querySelector('body').appendChild(rmenu);

  document.querySelector('.rmenu').style.display = 'block';
  document.querySelector('.rmenu').style.left = event.pageX + 'px';
  document.querySelector('.rmenu').style.top = event.pageY + 'px';

  event.preventDefault();

  // Event lister for click and escape key. Hide the right menu on trigger
  window.addEventListener('keydown', hideEscape);
  document.querySelector('body').addEventListener('click', hideClick);

  if (diff < 60000){
      document.querySelector('#recall').style.display = 'block';
  }
  else{
    document.querySelector('#recall').style.display = 'none';
  }
  // add event listener to menu options and pass in the message that was clicked on then execute msgupdate AJAX function
  document.querySelector('#delete').addEventListener('click', () => {
    msgupdate(id, element, 'delete');
  });
  document.querySelector('#recall').addEventListener('click', () => {
    msgupdate(id, element, 'recall');
  });
}
}

// Hides right click menu on click
function hideClick(){
  document.querySelector('.rmenu').remove();

  // remove event listener after execution
  document.querySelector('body').removeEventListener('click', hideClick);
}

// Hides right click menu on escape
function hideEscape(event){
  var keyCode = event.keyCode || event.which;
  if (event.keyCode == 27){
  document.querySelector('.rmenu').remove();

  // remove event listener after execution
  window.addEventListener('keydown', hideEscape);
  }
}

// Sends ajax request to server for recalled/deleted message to be updated in db`
function msgupdate(id, element, action) {

          // Initialize new request
          const request = new XMLHttpRequest();

          request.open('POST', '/recalldelete');

          // Callback function for when request completes
          request.onload = () => {

              // Extract JSON data from request

              const data = JSON.parse(request.responseText);

              // return true if success if error false
              if (data.success) {
                // apply styling for recall and recall message back to textarea
                if (action == 'recall'){
                  var recalledmsg = element.innerHTML;
                  element.innerHTML = "Message recalled"
                  element.setAttribute('class',"msg deleted-recalled");

                  document.querySelector('#message').value = recalledmsg;
                }
                // apply styling for deleted message
                else{
                  element.innerHTML = "Message deleted"
                  element.setAttribute('class',"msg deleted-recalled");
                }

              }
              else {
                document.querySelector('#error').innerHTML = 'Could not ' + action + ' delete message at this time';
              }
              // remove the event listeners after execution to prevent function being called again on the same element
              document.querySelector('#delete').removeEventListener('click', msgupdate);
              document.querySelector('#recall').removeEventListener('click', msgupdate);

              // remove right click rmenu
              document.querySelector('.remnu').remove();
          }

          // Add data to send with request
          const data = new FormData();
          data.append('id', id)
          data.append('action', action);

          // Send request
          request.send(data);
          return false;
}
