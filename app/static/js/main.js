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
    }
    
    start() {
        if (this.intervalId) return; // Non avviare due volte
        
        this.intervalId = setInterval(() => {
            this.remainingSeconds--;
            this.onTick(this.remainingSeconds);
            
            if (this.remainingSeconds <= 0) {
                this.stop();
                this.onComplete();
            }
        }, 1000);
    }
    
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    reset() {
        this.stop();
        this.remainingSeconds = this.initialSeconds;
    }
}

// Debug: log nel browser
console.log('✓ main.js caricato');
