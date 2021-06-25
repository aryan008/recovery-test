// https://codepen.io/figarali/pen/araWdP
jQuery(function($) {
 let path = window.location.href;
 $('ul a').each(function() {
  if (this.href === path) {
   $(this).addClass('active');
  }
 });
});


$('.score-percentage').each(function() {
    let tableScore = $(this);
    let score = tableScore.text()
    let numberScore = parseInt(score)
    

    if (numberScore >=70) {
        $(this).addClass( "recovered" );
    } else if (numberScore >= 50) {
        $(this).addClass( "moderate" );
    } else {
        $(this).addClass( "low" );
    }
}); 