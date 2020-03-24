//
let url = window.location.href;
if (!localStorage.getItem("displayname") && url != "http://127.0.0.1:5000/") {
  window.location.href= "/";
}

// If display name set then display display name, if not set redirect to home unless already on home page
document.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('displayname')){
    let name = localStorage.getItem('displayname');
    document.querySelector("#displayname").innerHTML = "posting as: " + name;
    document.querySelector("#displayname").style.padding = "5px";
  }
});

// If lastviewed url variable set then take the user back to that page and reset the variable if user didnt arrive via refresh or back/forward click
var p = performance.getEntriesByType("navigation");

if (p[0].type != 'reload' && p[0].type != 'back_forward'){
  if (localStorage.getItem('lastviewed')){
    if (localStorage.getItem('lastviewed') != ""){
      let url = localStorage.getItem('lastviewed');
      localStorage.setItem('lastviewed', "");
      if (confirm('Would you like to return to your last viewed channel?')){
          window.location.href= url;
      }
    }
  }

}
localStorage.setItem('lastviewed', "");
