// Listen for messages from the extension
chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === "playSound") playAudio(msg.play);
});

// Play sound with access to DOM APIs
function playAudio({ source, volume }) {
    const audio = new Audio(source);
    audio.volume = volume;
    audio.play();
}