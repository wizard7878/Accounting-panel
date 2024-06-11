var timeLeft = 59;
var elem = document.getElementById('some_div');

var timerId = setInterval(countdown, 1000);

function countdown() {
  if (timeLeft == -1) {
    clearTimeout(timerId);
    document.getElementById('send-sms-again').style.display = 'block';
    document.getElementById('otp-submit').style.display = 'none';
  } else {
    if (timeLeft >= 10){
        elem.innerHTML = `00:${timeLeft} ` ;
    }
    else{
      elem.innerHTML = `00:0${timeLeft} ` ;
    }
    timeLeft--;
  }
}