/*// --- Embedded JavaScript ---
function toggleDropdown() {
    const dropdown = document.getElementById("fatDropdown");
    dropdown.classList.toggle("open");
}

function toggleDropdownc() {
    const dropdown = document.getElementById("cDropdown");
    dropdown.classList.toggle("open");
}

// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("fatDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("cDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});
*/
// --- Embedded JavaScript ---
/*function toggleDropdown() {
    const dropdown = document.getElementById("fatDropdown");
    dropdown.classList.toggle("open");
}

function toggleDropdownc() {
    const dropdown = document.getElementById("cDropdown");
    dropdown.classList.toggle("open");
}

function toggleDropdownm() {
    const dropdown = document.getElementById("mDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("fatDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("cDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("mDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});*/
function toggleDropdownb() {
    const dropdown = document.getElementById("bDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("bDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

function toggleDropdown() {
    const dropdown = document.getElementById("fatDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("fatDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

function toggleDropdownc() {
    const dropdown = document.getElementById("cDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("cDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

function toggleDropdownm() {
    const dropdown = document.getElementById("mDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("mDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

function toggleDropdownl() {
    const dropdown = document.getElementById("lDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("lDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});

function toggleDropdownbo() {
    const dropdown = document.getElementById("boDropdown");
    dropdown.classList.toggle("open");
}
// Optional: close dropdown if clicked outside
window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("boDropdown");
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
    }
});



//------ To handle fat field in milk data --
function toggleFatField() {
    const fatField = document.getElementById('fatField');
    const buyRadio = document.querySelector('input[name="status"][value="buy"]');
    const sellRadio = document.querySelector('input[name="status"][value="sell"]');

    if (buyRadio.checked) {
        fatField.style.display = 'block';
    } else {
        fatField.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const radios = document.querySelectorAll('input[name="status"]');
    radios.forEach(radio => {
        radio.addEventListener('change', toggleFatField);
    });
});


    // JavaScript to handle the change in fat field requirement based on selected radio button status
    document.querySelectorAll('input[name="status"]').forEach(radio => {
        radio.addEventListener('change', function() {
            var fatField = document.getElementById('fat');
            var status = document.querySelector('input[name="status"]:checked').value;

            if (status === 'sell') {
                fatField.removeAttribute('required');  // Remove the required attribute
                fatField.value = 0;  // Set fat to 0
            } else {
                fatField.setAttribute('required', 'required');  // Make fat required again
            }
        });
    });

    // Trigger the change event when the page loads to apply the initial state

    