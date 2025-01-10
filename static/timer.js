// declare variables
let changeTime;
let isBreak;

let numberOfIntervals;
let currentInterval;

let breakMinutes;
let workMinutes;
let totalTime;
let intervalStarter;

// variables of tags in html file
const display = document.getElementById('countdown');
const start = document.getElementById('start');
const title = document.getElementById('indicator');

const form = document.getElementById("myForm")
const workForm = document.getElementById("work");
const breakForm = document.getElementById("break");
const intervalForm = document.getElementById("interval")



function setTotalTime(){

    // check if isbreak false
    if (isBreak == false){

        // change total time equal to inputted work time
        totalTime = workMinutes*60;

        //update html title
        title.innerHTML = 'WORK'
        currentInterval += 0.5

        isBreak = true;

    } else {

        // change total time equal to inputted break time
        totalTime = breakMinutes*60;

        //update break interval
        title.innerHTML = 'BREAK'
        currentInterval += 0.5

        isBreak = false;

    }

    
}

function updateCounter() {


    // check if current interval is less than number of interval requested
    if (currentInterval < numberOfIntervals){

        // if change time is true change time
        if (changeTime == true){
            setTotalTime();
            changeTime = false;
        }

        //  collect current time
        let currentMinutes = Math.floor(totalTime/60);
        let seconds = totalTime%60;

        //  if timer has ended, change time = true and break=true
        if (totalTime == 0){
            changeTime = true;
        }

        // if time is less than 10, add 0 to format
        if (seconds < 10) {
            display.innerHTML = currentMinutes + ":0"+ seconds;
        }

        else {
            display.innerHTML = currentMinutes + ":"+ seconds;
        }

        // decrease the time by 1
        totalTime -= 1;

    // else end the counter
    } else{
        endCounter()
    }
       
}

function endCounter(){

    // change end button into start timer
    start.innerHTML = "Start";
    start.classList.replace('btn-outline-danger', 'btn-outline-secondary');
    clearInterval(intervalStarter);

    start.removeEventListener("click", endCounter);
    start.addEventListener("click", startCounter);

    // enable forms
    formSwitch(false);

    // rest time and title
    display.innerHTML = "00:00";
    title.innerHTML = "TIMER";

    isBreak = false


}

function formSwitch(direction){

    // select all forms
    const inputs = form.querySelectorAll('input')

    // if direction true, disable all inputs
    if (direction == true){
        inputs.forEach(input  =>{
            input.disabled = true;
        });

    // else enable inputs and rest input fields
    } else{

        inputs.forEach(input  =>{
            input.disabled = false;
            input.value = '';
        });
    }
}

function startCounter(){

    // initialize variables use later
    changeTime = true;
    isBreak = false;
    currentInterval = 0;

    // set variables equal to inputted
    workMinutes = workForm.value;
    breakMinutes = breakForm.value;
    numberOfIntervals = intervalForm.value;

    // disable forms
    formSwitch(true);

    // Change start button into end timer
    start.innerHTML = "End";
    start.classList.replace('btn-outline-secondary', 'btn-outline-danger');
    start.removeEventListener("click", startCounter);
    start.addEventListener("click", endCounter);

    //Run update counter every 1 second
    intervalStarter = setInterval(updateCounter, 1000);
     
}

start.addEventListener("click", startCounter);





