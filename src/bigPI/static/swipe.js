document.addEventListener('DOMContentLoaded', () => {
    const messageBox = document.querySelector('.message-box');
    let startY, currentY, isDragging = false;

    messageBox.addEventListener('touchstart', startDrag);
    messageBox.addEventListener('touchmove', drag);
    messageBox.addEventListener('touchend', endDrag);

    messageBox.addEventListener('mousedown', startDrag);
    messageBox.addEventListener('mousemove', drag);
    messageBox.addEventListener('mouseup', endDrag);

    function startDrag(e) {
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
    }

    function endDrag() {
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
        setTimeout(() => {
            sendMessage();
            resetPosition();
        }, 300);
    }

    function sendMessage() {
        const messageContent = document.querySelector('textarea').value;
        const name = document.querySelector('#name').value;
        const datetime = document.querySelector('#datetime').value;

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
                'datetime': datetime
            })
        })
        .then(response => {
            if (response.ok) {
                console.log('Message sent successfully');
                // Clear the form fields
                document.querySelector('textarea').value = '';
                document.querySelector('#name').value = '';
                document.querySelector('#datetime').value = '';
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
        setTimeout(() => {
            messageBox.style.transition = 'transform 0.7s ease-out';
            messageBox.style.transform = 'translateY(0)';
        }, 50);
    }

    function smoothResetPosition() {
        messageBox.style.transition = 'transform 0.3s ease-out';
        messageBox.style.transform = 'translateY(0)';
    }
});