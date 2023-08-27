import 'htmx.org';
import Tagify from '@yaireo/tagify'

window.Tagify = Tagify

document.addEventListener("DOMContentLoaded", function(){
  // close side-menu when a link is clicked
  document.querySelectorAll("#side-menu a").forEach((elem) => {
    elem.addEventListener('click', (event) => {
      document.getElementById("side-menu").classList.remove("active");
    });
  });

  // Listen for `Hx-Trigger: {"toast": ...}` from the server and show a popup at the top of the screen
  document.body.addEventListener("toast", function(event){
    const eventClass = event.detail.type == "success" ? "is-success" : "is-danger";
    const template = document.createElement('template');
    template.innerHTML = `<div class="notification ${eventClass}">${event.detail.message}</div>`;
    document.getElementById('toast-container').append(...template.content.children);
    setTimeout(() => {toast.remove()}, 3000);
  })
});
