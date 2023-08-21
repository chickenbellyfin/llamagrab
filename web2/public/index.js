import 'htmx.org';
import $ from 'jquery';

$(function () {
  // slide side-menu in and out on mobile
  $('#expand-button').on('click', function(event) {
    $('#side-menu').toggleClass('active');
  });

  // close side-menu when a link is clicked
  $('#side-menu a').on('click', function(event){
    $('#side-menu').removeClass('active');
  })

  // dismiss all modals when background is clicked
  $(document).on('click', '.modal-background', function(event) {
    $(event.target.closest('.modal')).removeClass('is-active');
  });

  // Listen for `Hx-Trigger: {"toast": ...}` from the server and show a popup at the top of the screen
  $(document).on('toast', function(event) {
    const eventClass = event.detail.type == "success" ? "is-success" : "is-danger";
    const toast = $(`<div class="notification ${eventClass}">${event.detail.message}</div>`);
    $('#toast-container').append(toast);
    setTimeout(() => {toast.remove()}, 3000);
  });
});
