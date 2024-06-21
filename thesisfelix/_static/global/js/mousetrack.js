// Initialize global variables 
var lButtonsMT, timeEnter;
var sNames = '';
var sDT = '';
var sCurrent = '';
var sTypeReveal = 'cell';

// When page is loaded
window.addEventListener('DOMContentLoaded', () => {
    // Activate all mousetracking buttons
    lButtonsMT = document.getElementsByClassName(sTypeReveal);
    for (let i = 0; i < lButtonsMT.length; i++) {
        let elem = lButtonsMT[i];
        CreateMT(elem, elem.id);
    }

    // Decision Buttons 
    lDecBtns = document.getElementsByClassName("dec-btn");
    for (let i = 0; i < lDecBtns.length; i++) {
        let elem = lDecBtns[i];
        // Get column name from ID
        let dec = elem.id.split('-')[1];
        // Add on-click function 
        elem.addEventListener('click', () => {
            document.getElementById('sDec').value = dec;
            document.getElementById('sNames').value = sNames;
            document.getElementById('sDT').value = sDT;
            console.log('Submitting form with values:', {
                dec: dec,
                sNames: sNames,
                sDT: sDT
            });
            endPage();
        });
    }
    // Begin timer
    timeEnter = new Date();
    setInterval(() => {
        if (sCurrent != '') {
            let now = new Date();
            let dt = (now - timeEnter) / 1000;
            document.getElementById('test-text').innerHTML = `${sCurrent}:${dt}`;
        }
    }, 50);

    // Make sure the first row is visible when the page loads
    showFirstRow();
});

// *********************************************************************
// Function Name:   updateMT
// Functionality:   
//                  Updates global vars and inputs with latest active AOI
//
// input:           object id
//
// returns:         void
// *********************************************************************

function updateMT(id) {
    console.log('updateMT called with id:', id);
    // Store/update current time
    let now = new Date();
    let dt = now - timeEnter;
    timeEnter = now;
    // Save dwell time on AOI
    if (sDT.length > 0) {
        sDT = `${sDT},${dt}`;
    } else {
        sDT = `${dt}`;
        // If first fixation, also record time to first fixation
        document.getElementById('time2first').value = timeEnter - dt - startTime;
    }
    // Update to current label
    if (sNames.length > 0) {
        sNames = `${sNames},${id}`;
    } else {
        sNames = `${id}`;
    }
    console.log('sNames updated to:', sNames);
}

// *********************************************************************
// Function Name:   hideEverything
// Functionality:   
//                  Hides all the elements with the class name mt-tgt
//
// input:           object id
//
// returns:         void
// *********************************************************************

function hideEverything() {
    var tableContainer = document.getElementById('table-container');
    var rows = tableContainer.getElementsByClassName('row');

    // Iterate through all rows to identify and hide the second and third rows of lValues
    for (let i = 0; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.getElementsByClassName('mt-tgt');

        // Check if the row contains lValues by the presence of mt-tgt cells
        if (cells.length > 0) {
            // Keep the first row visible
            if (i == 0) {
                for (let j = 0; j < cells.length; j++) {
                    cells[j].classList.remove('hide');
                }
            } else {
                for (let j = 0; j < cells.length; j++) {
                    cells[j].classList.add('hide');
                }
            }
        }
    }
}

// *********************************************************************
// Function Name:   activateMT
// Functionality:   
//                  Activate the elements mt-tgt with class tgt
//
// input:           object id
//
// returns:         void
// *********************************************************************

function activateMT(tgt) {
    hideEverything();
    let lTgt = document.getElementsByClassName(`mt-tgt ${tgt}`);
    for (let i = 0; i < lTgt.length; i++) {
        lTgt[i].classList.remove('hide');
    }
}

// *********************************************************************
// Function Name:   CreateMT
// Functionality:   
//                  Converts an html element into a mousetracking element
//
// input:           elem, object
//
// returns:         void
// *********************************************************************

function CreateMT(elem, tgt) {
    if (elem.parentNode.rowIndex !== 0) { // Skip adding hover events for the first row
        elem.addEventListener("mouseenter", () => {
            elem.classList.add('hover');
            timeEnter = new Date();
            sCurrent = elem.id;
            console.log('mouseenter:', sCurrent);
            activateMT(tgt);
        });
        elem.addEventListener("mouseleave", () => {
            elem.classList.remove('hover');
            updateMT(elem.id);
            sCurrent = ''; // Move this line below updateMT to ensure the current element is recorded
            console.log('mouseleave:', sCurrent);
            hideEverything();
            showFirstRow(); // Ensure the first row is always visible
        });
    }
}

// *********************************************************************
// Function Name:   showFirstRow
// Functionality:   
//                  Ensures the first row is always visible
//
// input:           none
//
// returns:         void
// *********************************************************************

function showFirstRow() {
    var tableContainer = document.getElementById('table-container');
    var firstRow = tableContainer.getElementsByClassName('row')[0];
    var cells = firstRow.getElementsByClassName('mt-tgt');
    for (let i = 0; i < cells.length; i++) {
        cells[i].classList.remove('hide');
    }
}

// *********************************************************************
// Function Name:   endDecPage
// Functionality:   
//                  function for the decision button/key
//
// input:           dec, decision to be recorded in variable
//
// returns:         void
// *********************************************************************

function endDecPage(dec) {
    // Store all mousetracking variables + decision for the page
    document.getElementById('iDec').value = dec;
    document.getElementById('sNames').value = sNames;
    document.getElementById('sDT').value = sDT;
    console.log('endDecPage:', dec, sNames, sDT);
    endPage();
}
