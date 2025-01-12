// Declare variables
let changeTime;
let isBreak;

let numberOfIntervals;
let currentInterval;

let breakMinutes;
let workMinutes;
let totalTime;
let intervalStarter;

// Variables of tags in HTML file
const display = document.getElementById('countdown');
const start = document.getElementById('start');
const title = document.getElementById('indicator');

const form = document.getElementById("myForm")
const workForm = document.getElementById("work");
const breakForm = document.getElementById("break");
const intervalForm = document.getElementById("interval")



function setTotalTime(){

    // Check if isbreak false
    if (isBreak == false){

        // Change total time equal to inputted work time
        totalTime = workMinutes*60;

        // Update html title
        title.innerHTML = 'WORK'
        currentInterval += 0.5

        isBreak = true;

    } else {

        // Change total time equal to inputted break time
        totalTime = breakMinutes*60;

        // Update break interval
        title.innerHTML = 'BREAK'
        currentInterval += 0.5

        isBreak = false;

    }

    
}

function updateCounter() {


    //Check if the current interval is less than the number of intervals requested
    if (currentInterval < numberOfIntervals){

        //If change time is true change time
        if (changeTime == true){
            setTotalTime();
            changeTime = false;
        }

        //  Collect current time
        let currentMinutes = Math.floor(totalTime/60);
        let seconds = totalTime%60;

        //  If timer has ended, change time = true and break=true
        if (totalTime == 0){
            changeTime = true;
        }

        // If time is less than 10, add 0 to format
        if (seconds < 10) {
            display.innerHTML = currentMinutes + ":0"+ seconds;
        }

        else {
            display.innerHTML = currentMinutes + ":"+ seconds;
        }

        // Decrease the time by 1
        totalTime -= 1;

    // Else end the counter
    } else{
        endCounter()
    }
       
}

function endCounter(){

    // Change the end button to start timer
    start.innerHTML = "Start";
    start.classList.replace('btn-outline-danger', 'btn-outline-secondary');
    clearInterval(intervalStarter);

    start.removeEventListener("click", endCounter);
    start.addEventListener("click", startCounter);

    // Enable forms
    formSwitch(false);

    // Rest time and title
    display.innerHTML = "00:00";
    title.innerHTML = "TIMER";

    isBreak = false


}

function formSwitch(direction){

    // Select all forms
    const inputs = form.querySelectorAll('input')

    // If direction true, disable all inputs
    if (direction == true){
        inputs.forEach(input  =>{
            input.disabled = true;
        });

    // Else enable inputs and rest input fields
    } else{

        inputs.forEach(input  =>{
            input.disabled = false;
            input.value = '';
        });
    }
}

function startCounter(){

    // Initialize variables use later
    changeTime = true;
    isBreak = false;
    currentInterval = 0;

    // Set variables equal to inputted
    workMinutes = workForm.value;
    breakMinutes = breakForm.value;
    numberOfIntervals = intervalForm.value;

    // Disable forms
    formSwitch(true);

    // Change the start button to end timer
    start.innerHTML = "End";
    start.classList.replace('btn-outline-secondary', 'btn-outline-danger');
    start.removeEventListener("click", startCounter);
    start.addEventListener("click", endCounter);

    // Run update counter every 1 second
    intervalStarter = setInterval(updateCounter, 1000);
     
}

start.addEventListener("click", startCounter);





