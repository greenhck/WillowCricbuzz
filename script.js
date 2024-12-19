const PROXY_URL = "https://cors-anywhere.herokuapp.com/"; // Public proxy URL
const playButton = document.getElementById('playButton');
const videoPlayer = videojs('videoPlayer');

playButton.addEventListener('click', () => {
    const videoUrl = document.getElementById('videoLink').value.trim();

    if (!videoUrl) {
        alert("Please enter a valid video URL!");
        return;
    }

    // Combine proxy URL with the user's video URL
    const proxiedUrl = PROXY_URL + videoUrl;

    // Load the video in the player
    videoPlayer.src({ src: proxiedUrl, type: 'application/x-mpegURL' });
    videoPlayer.play();
});
