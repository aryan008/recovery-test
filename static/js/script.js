// https://codepen.io/figarali/pen/araWdP
jQuery(function($) {
 let path = window.location.href;
 $('ul a').each(function() {
  if (this.href === path) {
   $(this).addClass('active');
  }
 });
});