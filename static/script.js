document.addEventListener("DOMContentLoaded", function() {
    const hamBtn = document.querySelector('.ham-btn');
    const hamBox = document.querySelector('.ham-box');
    const body = document.querySelector('body');

    // Function to open ham-box
    function openHamBox() {
        hamBox.classList.remove('ham-box-hidden');
        body.classList.add('ham-box-opened');
        document.addEventListener('click', closeHamBoxOnClickOutside);
        document.addEventListener('keydown', closeHamBoxOnEsc);
    }

    // Function to close ham-box
    function closeHamBox() {
        hamBox.classList.add('ham-box-hidden');
        body.classList.remove('ham-box-opened');
        document.removeEventListener('click', closeHamBoxOnClickOutside);
        document.removeEventListener('keydown', closeHamBoxOnEsc);
    }

    // Function to close ham-box when clicking outside of it
    function closeHamBoxOnClickOutside(event) {
        if (!hamBox.contains(event.target) && event.target !== hamBtn) {
            closeHamBox();
        }
    }

    // Function to close ham-box when pressing escape key
    function closeHamBoxOnEsc(event) {
        if (event.key === 'Escape') {
            closeHamBox();
        }
    }

    // Event listener for ham-btn click
    hamBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        if (hamBox.classList.contains('ham-box-hidden')) {
            openHamBox();
        } else {
            closeHamBox();
        }
    });

    // Event listener to close ham-box if already opened
    body.addEventListener('click', function(event) {
        if (!hamBox.classList.contains('ham-box-hidden') && event.target !== hamBtn) {
            closeHamBox();
        }
    });
});
