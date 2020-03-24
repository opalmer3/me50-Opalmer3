// enable submit button when input field length greater than 0
document.querySelector("#newChannelForm input[name='name']").addEventListener('keyup', () => {

    let input = document.querySelector("#newChannelForm input[name='name']").value;

  if (input.length > 0){
    document.querySelector("#newChannelForm button[type='submit']").disabled = false;
  }
  else{
    document.querySelector("#newChannelForm button[type='submit']").disabled = true;
  }
});

// Set value of button to displayname if display name not set redirect to homepage
document.addEventListener('DOMContentLoaded', () => {
  if (!localStorage.getItem('displayname')){
    window.location.href="/";
  }
  else {
    let name = localStorage.getItem('displayname');
    document.querySelector("#newChannelForm button").setAttribute('value', name);
  }

});
