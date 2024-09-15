document.addEventListener('DOMContentLoaded', () => {
    const messageBox = document.querySelector('.message-box');
    const canvas = document.getElementById('drawingCanvas');
    let startY, currentY, isDragging = false;

    // Add these lines to get the header text element
    const headerText = document.querySelector('.header-text');

    // Use document instead of messageBox for event listeners
    document.addEventListener('touchstart', startDrag, { passive: false });
    document.addEventListener('touchmove', drag, { passive: false });
    document.addEventListener('touchend', endDrag);

    document.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);

    function startDrag(e) {
        // Prevent dragging if the event target is the canvas or its child
        if (e.target === canvas || canvas.contains(e.target)) {
            return;
        }
        e.preventDefault(); // Prevent default touch behavior
        startY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
        currentY = startY; // Initialize currentY
        isDragging = true;
        messageBox.style.transition = 'none';
    }

    function drag(e) {
        if (!isDragging) return;
        e.preventDefault();
        currentY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
        const deltaY = startY - currentY;
        messageBox.style.transform = `translateY(-${Math.max(0, deltaY)}px)`;

        // Adjust header text opacity based on swipe progress
        const progress = Math.min(deltaY / (window.innerHeight / 3), 1);
        headerText.style.opacity = 1 - progress;
    }

    function endDrag(e) {
        if (!isDragging) return;
        isDragging = false;
        const deltaY = startY - currentY;
        messageBox.style.transition = 'transform 0.3s ease-out';
        if (deltaY > window.innerHeight / 3 && deltaY !== 0) { // Check if deltaY is not 0
            swipeUp();
        } else {
            smoothResetPosition();
        }
    }

    function swipeUp() {
        messageBox.style.transform = `translateY(-${window.innerHeight}px)`;
        headerText.style.opacity = 0; // Hide header text completely
        setTimeout(() => {
            sendMessage();
            resetPosition();
        }, 300);
    }

    function sendMessage() {
        const messageContent = document.querySelector('textarea').value;
        const name = document.querySelector('#name').value;
        const datetime = document.querySelector('#datetime').value;
        const pixelData = document.querySelector('#pixelData').value;

        if (!messageContent || !name || !datetime) {
            alert('Please fill in all fields before submitting.');
            return;
        }

        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'message': messageContent,
                'name': name,
                'datetime': datetime,
                'pixelData': pixelData
            })
        })
        .then(response => {
            if (response.ok) {
                console.log('Message sent successfully');
                // Clear the form fields
                document.querySelector('textarea').value = '';
                document.querySelector('#name').value = '';
                document.querySelector('#datetime').value = '';
                document.querySelector('#pixelData').value = '';
                // Trigger candy rain
                createCandyRain();
            } else {
                console.error('Failed to send message');
                alert('Failed to send message. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }

    function resetPosition() {
        messageBox.style.transition = 'none';
        messageBox.style.transform = 'translateY(100%)';
        headerText.style.opacity = 1; // Show header text again
        setTimeout(() => {
            messageBox.style.transition = 'transform 0.7s ease-out';
            messageBox.style.transform = 'translateY(0)';
        }, 50);
    }

    function smoothResetPosition() {
        messageBox.style.transition = 'transform 0.3s ease-out';
        messageBox.style.transform = 'translateY(0)';
        headerText.style.opacity = 1; // Ensure header text is fully visible
    }

    function createCandyRain() {
        const candyContainer = document.getElementById('candyContainer');
        const candyCount = 50;

        for (let i = 0; i < candyCount; i++) {
            const candy = document.createElement('div');
            candy.className = 'candy';
            candy.style.left = `${Math.random() * 100}vw`;
            candy.style.animationDuration = `${Math.random() * 2 + 1}s`;
            candy.style.animationDelay = `${Math.random() * 0.5}s`;
            candyContainer.appendChild(candy);

            candy.addEventListener('animationend', () => {
                candy.remove();
            });
        }
    }
});