/**
 * Main JavaScript - Utilità globali e logica condivisa
 */

// Funzione per formattare i secondi in MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// Inizia un timer e richiama un callback quando finisce
class RoundTimer {
    constructor(initialSeconds, onTick, onComplete) {
        this.initialSeconds = initialSeconds;
        this.remainingSeconds = initialSeconds;
        this.onTick = onTick;
        this.onComplete = onComplete;
        this.intervalId = null;
        this.audio = null;
    }
    
    setAudio(audioSrc) {
        this.audio = new Audio(audioSrc);
        this.audio.loop = false;
    }
    
    _stopInterval() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    start() {
        if (this.intervalId) return; // Non avviare due volte
        
        // Avvia l'audio se impostato
        if (this.audio) {
            this.audio.currentTime = 0;
            this.audio.play().catch(e => console.warn('Audio play bloccato:', e));
        }
        
        this.intervalId = setInterval(() => {
            this.remainingSeconds--;
            this.onTick(this.remainingSeconds);
            
            if (this.remainingSeconds <= 0) {
                this._stopInterval(); // Ferma solo il timer, non l'audio
                this.onComplete();
            }
        }, 1000);
    }
    
    stop() {
        this._stopInterval();
        // Ferma l'audio
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
        }
    }
    
    reset() {
        this.stop();
        this.remainingSeconds = this.initialSeconds;
    }
}

// Funzione helper per riprodurre un audio da startTime a endTime
function playAudioSegment(audioSrc, startTime, endTime) {
    const audio = new Audio(audioSrc);
    audio.currentTime = startTime;
    
    const checkEnd = () => {
        if (audio.currentTime >= endTime) {
            audio.pause();
            audio.currentTime = 0;
            audio.removeEventListener('timeupdate', checkEnd);
        }
    };
    
    audio.addEventListener('timeupdate', checkEnd);
    audio.play().catch(e => console.warn('Audio play bloccato:', e));
}

// Debug: log nel browser
console.log('✓ main.js caricato');
