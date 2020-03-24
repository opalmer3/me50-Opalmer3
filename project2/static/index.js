// If display name not set create a form to enter display name.
document.addEventListener('DOMContentLoaded', () => {
  if (!localStorage.getItem('displayname')){
    // Create form element
    const message = document.createElement('h3');
    message.innerHTML = "Enter a display name to view, create and participate in conversations"

    const form = document.createElement('form');
    form.setAttribute('id', "myForm");
    form.setAttribute('method', "post")
    form.setAttribute('autocomplete', "off")

    // Create input element
    const input = document.createElement('input');
    input.setAttribute('type', "text");
    input.setAttribute('name', "displayname");
    input.setAttribute('placeholder', "Display name");
    input.setAttribute('required', "required");

    // Create button element
    const button = document.createElement('button');
    button.setAttribute('type', "submit");
    button.setAttribute('id', "submit");
    button.setAttribute('disabled', "true");
    button.setAttribute('class', "btn btn-dark");
    button.innerHTML = "Submit";

    // Append input and button to form
    form.appendChild(input);
    form.appendChild(button);

    document.querySelector("#displayform").appendChild(message);
    document.querySelector("#displayform").appendChild(form);

  }
else{
  let name = localStorage.getItem('displayname');
  const message = document.createElement('h3');
  message.innerHTML = "Hi " + name + ", thanks for using All Chat! Feel free to start a new conversation and join ongoing conversations!"

  const form = document.createElement('form');
  form.setAttribute('action', "/newchannel");

  const button = document.createElement('button');
  button.setAttribute('type', "submit");
  button.setAttribute('class', "btn btn-dark");
  button.innerHTML = "Start a new conversation";

  form.appendChild(button);

  const hr = document.createElement('hr');

  document.querySelector('#welcome').appendChild(message);
  document.querySelector('#welcome').appendChild(hr);
  document.querySelector('#welcome').appendChild(form);
}
});

// enable submit button when input field length greater than 0
document.addEventListener('keyup', e => {
  if (e.target.name === 'displayname') {
    let input = document.querySelector("#myForm input[name='displayname']").value;

    if (input.length > 0) {
      document.querySelector("#myForm button[type='submit']").disabled = false;
    } else {
      document.querySelector("#myForm button[type='submit']").disabled = true;
    }
  }
});

// When form submitted store display name in local localStorage
document.addEventListener('submit', e => {
  if (e.target.id === 'myForm'){
    let input = document.querySelector("#myForm input[name='displayname']").value;
    localStorage.setItem('displayname', input);
    e.preventDefault();
    location.reload();
  }
})

//Add link functionality to table rows
document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('tbody tr').onclick = function (){
    const link = this.firstElementChild.firstElementChild.getAttribute('href');
    window.location.href = link;
  }
});
