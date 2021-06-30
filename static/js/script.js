/**
* @fileOverview Recovery Pod script.js file.
* @author <a href="https://github.com/aryan008">Adam Ryan</a>
* @version 1.1.1
*/
/*jshint esversion: 6 */

/* The below function adds the class of "active" to the current window location the site user is on */
// https://codepen.io/figarali/pen/araWdP
jQuery(function ($) {
    // find the window location the user is currently on
    let path = window.location.href;
    // for loop to apply a function to each "ul a" tag
    $('ul a').each(function () {
        if (this.href === path) {
            // add the class of active if this href is the window location
            $(this).addClass('active');
        }
    });
});

/* The below function applies the correct class to the score of the user for all entries */
$('.score-percentage').each(function() {
    let tableScore = $(this);
    // get the score of each entry
    let score = tableScore.text()
    // convert each score to numerical
    let numberScore = parseInt(score)
    
    // apply appropriate classes depending on the score
    if (numberScore >=70) {
        $(this).addClass( "recovered" );
    } else if (numberScore >= 50) {
        $(this).addClass( "moderate" );
    } else {
        $(this).addClass( "low" );
    }
}); 

/* The below function applies the correct class to the score of the user for todays entry.
Logic and code sourced from: https://stackoverflow.com/questions/21727317/how-to-check-confirm-password-field-in-form-without-reloading-page/21727518 */
$('.result-container').each(function() {
    // grab the result the user got
    let userScore = $(".inner-container p");
    // get rid of the percent sign
    let splitScore = userScore.text().split("%")
    // convert the score to an integer
    let actualScore = parseInt(splitScore[0])
    
    // apply appropriate classes depending on the score
    if (actualScore >=70) {
        $(this).addClass( "recovered" );
    } else if (actualScore >= 50) {
        $(this).addClass( "moderate" );
    } else {
        $(this).addClass( "low" );
    }
});

/* The below function checks that the password reset feature works appropriately*/
function passwordCheck() {
    // get the new password
    let password = document.querySelector('#newpassword');
    // get the reentered password
    let confirm = document.querySelector('#confirmpassword');
    // if they are the same, update the password. If not, let the user know the passwords dont match
    if(confirm.value == password.value) {
        confirm.setCustomValidity('');
    } else {
        confirm.setCustomValidity('New password does not match the re-entered value');
    }
}