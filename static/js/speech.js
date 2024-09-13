document.addEventListener('DOMContentLoaded', function() {
    const speechButton = document.getElementById('speechRecognition');
    const symptomsInput = document.querySelector('input[name="symptoms"]');

    speechButton.addEventListener('click', function() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.start();

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            symptomsInput.value = transcript;
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };
    });
});