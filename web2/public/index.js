import 'htmx.org';
import $ from 'jquery';

$(function () {
  // Check for click events on the navbar burger icon
  $(".navbar-burger").click(function () {
    // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
  });

  // when nav menu is clicked on mobile, hide it
  $(".navbar-menu a").click(function(event){
    $(".navbar-menu").removeClass("is-active");
    $(".navbar-burger").removeClass("is-active");
    event.target.blur(); 
    
  })

  // Listen for `Hx-Trigger: {"toast": ...}` from the server and show a popup at the top of the screen
  document.body.addEventListener("toast", function(evt){
    var toast = document.createElement('div');
    const eventType = evt.detail.type == "success" ? "is-success" : "is-danger";
    toast.className = `notification ${eventType}`;
    toast.textContent = evt.detail.message;
    toast.setAttribute('remove-me', '2s');
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => { toast.remove() }, 2000)
  })
});
