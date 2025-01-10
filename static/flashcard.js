
// variables for tags in html
const add_card_button = document.getElementById('add-card');
const remove_card_button = document.getElementById('remove-card');

const div_container = document.getElementById('input-container');

// variables
 let cardIndex = 5;
 let term = 'Term';
 let defin = 'Definition';

function add_flash_card_inputs() {
    //Create div container for input values
    const newDiv = document.createElement("div");
    newDiv.className = "row mt-4 justify-content-around";
    newDiv.id = "div-input"

    //Create input values to append to the new div
    const newInputTerm = document.createElement("input");
    newInputTerm.className = "col-5 form-control-lg text-center ml-5";
    newInputTerm.placeholder = term;
    newInputTerm.setAttribute("name", term.concat(cardIndex))
    newInputTerm.required = true;

    // input for definition
    const newInputDefinition = document.createElement("input");
    newInputDefinition.className = "col-5 form-control-lg text-center ml-5";
    newInputDefinition.placeholder = defin;
    newInputDefinition.setAttribute("name", defin.concat(cardIndex));
    newInputDefinition.required = true;

    //insert the new inputs inside the container
    div_container.insertBefore(newDiv, document.getElementById('button-row'));
    newDiv.append(newInputTerm);
    newDiv.append(newInputDefinition);

    //increase current index of items
    cardIndex++;

}


function remove_card(){



    // remove card if there are any cards
    if (cardIndex > 0){
       // collect all div inputs

        const divs = document.querySelectorAll('#div-input');

        // remove the last item from the divs
        divs[divs.length-1].remove();

        // decrease index counter
         cardIndex--;
    }

}

remove_card_button.addEventListener("click", remove_card);
add_card_button.addEventListener("click", add_flash_card_inputs);