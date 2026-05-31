// 🔮 Witching Hour Poker 🔮
// Client-Side Game Loop, Dynamic 6-Player Seating, and Web Audio API Synthesis

/**
 * SoundSynth
 * Web Audio API synthesizer for dependency-free, high-fidelity magical sound effects.
 */
class SoundSynth {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.muted = false;
        this.volume = 0.5; // Default 50%
        this.bubbleTimer = null;
    }

    /**
     * Initializes the AudioContext lazily on user interaction
     */
    init() {
        if (this.ctx) return;
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContextClass();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.setValueAtTime(this.muted ? 0 : this.volume, this.ctx.currentTime);
            this.masterGain.connect(this.ctx.destination);
            
            // Start continuous gentle bubbling of cauldron!
            this.startBubbling();
        } catch (e) {
            console.error("Web Audio API not supported in this browser:", e);
        }
    }

    resume() {
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    setVolume(vol) {
        this.volume = vol;
        if (this.masterGain && !this.muted) {
            this.masterGain.gain.setValueAtTime(vol, this.ctx.currentTime);
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        if (this.masterGain) {
            this.masterGain.gain.setValueAtTime(this.muted ? 0 : this.volume, this.ctx.currentTime);
        }
        return this.muted;
    }

    /**
     * SFX 1: Card Deal / Rustle
     * Synthesizes the sliding flip of a parchment card.
     */
    playDeal() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;

        // 1. Friction white noise
        const bufferSize = this.ctx.sampleRate * 0.12; // 120ms
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }

        const noiseNode = this.ctx.createBufferSource();
        noiseNode.buffer = buffer;

        const noiseFilter = this.ctx.createBiquadFilter();
        noiseFilter.type = 'bandpass';
        noiseFilter.frequency.setValueAtTime(1000, now);
        noiseFilter.frequency.exponentialRampToValueAtTime(1600, now + 0.1);
        noiseFilter.Q.setValueAtTime(8, now);

        const noiseGain = this.ctx.createGain();
        noiseGain.gain.setValueAtTime(0.06, now);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

        // 2. Tonal flip sound
        const osc = this.ctx.createOscillator();
        const oscGain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(750, now);
        osc.frequency.exponentialRampToValueAtTime(180, now + 0.08);

        oscGain.gain.setValueAtTime(0.12, now);
        oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

        // Wiring
        noiseNode.connect(noiseFilter);
        noiseFilter.connect(noiseGain);
        noiseGain.connect(this.masterGain);

        osc.connect(oscGain);
        oscGain.connect(this.masterGain);

        noiseNode.start(now);
        noiseNode.stop(now + 0.12);
        osc.start(now);
        osc.stop(now + 0.08);
    }

    /**
     * SFX 2: Spell Swell (Raise / Active Action)
     * Synthesizes a magic energy build-up.
     */
    playSpell() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;
        const duration = 0.55;

        const osc = this.ctx.createOscillator();
        const filter = this.ctx.createBiquadFilter();
        const gainNode = this.ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(130, now);
        osc.frequency.exponentialRampToValueAtTime(420, now + duration);

        filter.type = 'lowpass';
        filter.Q.setValueAtTime(12, now);
        filter.frequency.setValueAtTime(200, now);
        filter.frequency.exponentialRampToValueAtTime(1600, now + duration);

        gainNode.gain.setValueAtTime(0.001, now);
        gainNode.gain.linearRampToValueAtTime(0.12, now + duration * 0.4);
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);

        osc.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.masterGain);

        osc.start(now);
        osc.stop(now + duration);
    }

    /**
     * SFX 3: Magical Chimes
     * Cascading, glistening wind chimes of high pentatonic registers.
     */
    playChimes() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;
        const freqs = [880, 987.77, 1174.66, 1318.51, 1567.98, 1760, 2093];

        freqs.forEach((freq, index) => {
            const delay = index * 0.07;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const filter = this.ctx.createBiquadFilter();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + delay);

            filter.type = 'highpass';
            filter.frequency.setValueAtTime(600, now + delay);

            gain.gain.setValueAtTime(0.001, now + delay);
            gain.gain.linearRampToValueAtTime(0.05, now + delay + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.6);

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(this.masterGain);

            osc.start(now + delay);
            osc.stop(now + delay + 0.7);
        });
    }

    /**
     * SFX 4: Bubble Pop
     * Low pitch bubble expansion and pop.
     */
    playBubble() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        const baseFreq = 65 + Math.random() * 45;
        const endFreq = 230 + Math.random() * 70;
        const duration = 0.09 + Math.random() * 0.11;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(baseFreq, now);
        osc.frequency.exponentialRampToValueAtTime(endFreq, now + duration);

        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(now);
        osc.stop(now + duration);
    }

    /**
     * SFX 5: Double Wood Knock (Check)
     */
    playKnock() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;

        [0, 0.13].forEach(delay => {
            const osc = this.ctx.createOscillator();
            const filter = this.ctx.createBiquadFilter();
            const gain = this.ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(115, now + delay);
            osc.frequency.exponentialRampToValueAtTime(40, now + delay + 0.04);

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(240, now + delay);

            gain.gain.setValueAtTime(0.18, now + delay);
            gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.05);

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(this.masterGain);

            osc.start(now + delay);
            osc.stop(now + delay + 0.06);
        });
    }

    /**
     * SFX 6: Victory arpeggio
     */
    playVictory() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;
        const chord = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50];

        chord.forEach((freq, index) => {
            const delay = index * 0.09;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const filter = this.ctx.createBiquadFilter();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + delay);

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(1400, now + delay);

            gain.gain.setValueAtTime(0.001, now + delay);
            gain.gain.linearRampToValueAtTime(0.07, now + delay + 0.04);
            gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 1.1);

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(this.masterGain);

            osc.start(now + delay);
            osc.stop(now + delay + 1.3);
        });
    }

    /**
     * SFX 7: Fold / Ash Burn
     */
    playBurn() {
        this.init();
        this.resume();
        if (!this.ctx || this.muted) return;

        const now = this.ctx.currentTime;
        const duration = 0.42;

        const bufferSize = this.ctx.sampleRate * duration;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }

        const source = this.ctx.createBufferSource();
        source.buffer = buffer;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(850, now);
        filter.frequency.linearRampToValueAtTime(120, now + duration);
        filter.Q.setValueAtTime(6, now);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

        source.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterGain);

        source.start(now);
        source.stop(now + duration);
    }

    startBubbling() {
        if (this.bubbleTimer) clearInterval(this.bubbleTimer);
        // Periodically trigger ambient cauldron bubbling
        this.bubbleTimer = setInterval(() => {
            if (!this.muted && this.ctx && this.ctx.state === 'running') {
                const count = Math.floor(Math.random() * 3) + 1;
                for (let i = 0; i < count; i++) {
                    setTimeout(() => this.playBubble(), Math.random() * 500);
                }
            }
        }, 2200);
    }
}


// --- Main Application Orchestration ---
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const cardsContainer = document.getElementById('cards');
    const playerSeatsContainer = document.getElementById('player-seats');
    const handRankElement = document.getElementById('hand-rank');
    const balanceElement = document.getElementById('balance');
    const potAmountElement = document.getElementById('pot-amount');
    const phaseDisplay = document.getElementById('phase-display');
    const deckCountElement = document.getElementById('deck-count');
    const betAmountInput = document.getElementById('bet-amount');
    
    const dealBtn = document.getElementById('deal-btn');
    const drawBtn = document.getElementById('draw-btn');
    const bettingActions = document.getElementById('betting-actions');
    const foldBtn = document.getElementById('fold-btn');
    const callBtn = document.getElementById('call-btn');
    const raiseBtn = document.getElementById('raise-btn');
    const shuffleBtn = document.getElementById('shuffle-btn');
    const resetBtn = document.getElementById('reset-btn');
    
    const themeToggle = document.getElementById('theme-toggle');
    const autoplayToggle = document.getElementById('autoplay-toggle');
    const soundToggle = document.getElementById('sound-toggle');
    const soundIcon = document.getElementById('sound-icon');
    const volumeSlider = document.getElementById('volume-slider');
    
    const body = document.body;

    // Instantiations & State
    const audio = new SoundSynth();
    let heldIndices = [];
    let currentPhase = 'waiting';
    let playerId = 'player1';
    let lastCardsJson = '';
    let lastOpponentsJson = '';
    let isAutoplayActive = false;
    let autoplayTimer = null;
    
    // Message mapping and state trackers
    const processedMsgIds = new Set();
    let isInitialChatLoadDone = false;

    const botNameMap = {
        'player1': 'You',
        'bot1': 'Rhiannon',
        'bot2': 'Althea',
        'bot3': 'Zephyr',
        'bot4': 'Madrigal',
        'bot5': 'Morrigan',
        'system': 'Coven Sentinel'
    };

    // Unlock Web Audio Context on document interactions (browser policy bypass)
    ['click', 'mousedown', 'keydown', 'touchstart'].forEach(event => {
        document.body.addEventListener(event, () => {
            audio.init();
            audio.resume();
        }, { once: true });
    });

    // Theme Toggle (Moonlight vs Witchy Night)
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('light-mode');
        const isMoonlight = body.classList.contains('light-mode');
        themeToggle.innerHTML = isMoonlight ? '<i class="fas fa-sun"></i> Witchy Night' : '<i class="fas fa-moon"></i> Moonlight';
        localStorage.setItem('theme', isMoonlight ? 'moonlight' : 'witchy');
    });

    // Initialize saved theme
    if (localStorage.getItem('theme') === 'moonlight') {
        body.classList.add('light-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i> Witchy Night';
    }

    // Autoplay (Oracle Mode) Toggle
    autoplayToggle.addEventListener('click', async () => {
        audio.init();
        audio.resume();
        try {
            const response = await fetch('/autoplay/toggle', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                isAutoplayActive = data.autoplay;
                if (isAutoplayActive) {
                    autoplayToggle.classList.add('active');
                    autoplayToggle.innerHTML = '<i class="fas fa-magic"></i> Auto-Playing...';
                    audio.playChimes();
                    runAutoplayStep();
                } else {
                    autoplayToggle.classList.remove('active');
                    autoplayToggle.innerHTML = '<i class="fas fa-magic"></i> Oracle Mode (AI)';
                    if (autoplayTimer) {
                        clearTimeout(autoplayTimer);
                        autoplayTimer = null;
                    }
                    audio.playDeal();
                }
                // Refresh state immediately to hide/show controls
                await fetchState();
            }
        } catch (error) {
            console.error('Error toggling autoplay:', error);
        }
    });

    function runAutoplayStep() {
        if (!isAutoplayActive) return;
        
        // Use a longer delay on waiting/showdown phase so the user can see cards/results
        const delay = currentPhase === 'waiting' ? 4000 : 2500;
        
        autoplayTimer = setTimeout(async () => {
            if (!isAutoplayActive) return;
            try {
                const response = await fetch('/autoplay/step', { method: 'POST' });
                if (response.ok) {
                    const data = await response.json();
                    updateUI(data);
                    await fetchChatMessages();
                }
            } catch (error) {
                console.error('Error in autoplay step:', error);
            }
            // Queue next step
            runAutoplayStep();
        }, delay);
    }

    // Sound Slider and Mute Buttons
    soundToggle.addEventListener('click', () => {
        audio.init();
        audio.resume();
        const isMuted = audio.toggleMute();
        soundIcon.className = isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
        soundToggle.title = isMuted ? 'Unmute Soundscape' : 'Mute Soundscape';
    });

    volumeSlider.addEventListener('input', (e) => {
        audio.init();
        audio.resume();
        const vol = parseInt(e.target.value) / 100;
        audio.setVolume(vol);
        if (audio.muted && vol > 0) {
            audio.toggleMute();
            soundIcon.className = 'fas fa-volume-up';
        }
    });

    // Run first state fetches
    fetchState();
    fetchChatMessages();

    async function fetchState() {
        try {
            const response = await fetch(`/state?player_id=${playerId}`);
            if (response.ok) {
                const data = await response.json();
                updateUI(data);
            }
        } catch (error) {
            console.error('Error fetching table state:', error);
        }
    }

    function updateUI(data) {
        // Sync autoplay state with backend
        if (data.autoplay !== undefined) {
            const backendAutoplay = !!data.autoplay;
            if (backendAutoplay !== isAutoplayActive) {
                isAutoplayActive = backendAutoplay;
                if (isAutoplayActive) {
                    autoplayToggle.classList.add('active');
                    autoplayToggle.innerHTML = '<i class="fas fa-magic"></i> Auto-Playing...';
                    runAutoplayStep();
                } else {
                    autoplayToggle.classList.remove('active');
                    autoplayToggle.innerHTML = '<i class="fas fa-magic"></i> Oracle Mode (AI)';
                    if (autoplayTimer) {
                        clearTimeout(autoplayTimer);
                        autoplayTimer = null;
                    }
                }
            }
        }

        const me = data.players.find(p => p.id === playerId);
        const opponents = data.players.filter(p => p.id !== playerId);

        // Update Grimoire metrics
        balanceElement.innerHTML = `<span>💎 Crystals:</span> <span class="val">$${me.balance}</span>`;
        potAmountElement.textContent = `$${data.pot}`;
        phaseDisplay.innerHTML = `<span>🌒 Moon Phase:</span> <span class="val">${formatPhase(data.phase)}</span>`;
        deckCountElement.innerHTML = `<span>🎴 Deck Count:</span> <span class="val">${data.deck_count} Cards</span>`;
        currentPhase = data.phase;

        // Turn announcements
        const isMyTurn = data.active_player_id === playerId;
        const playerActionDisplay = document.getElementById('player-action-display');
        if (isMyTurn) {
            playerActionDisplay.textContent = '🔮 YOUR TURN TO CAST';
            playerActionDisplay.style.color = '#39ff14'; // Radiant Emerald
        } else {
            const activePlayer = data.players.find(p => p.id === data.active_player_id);
            playerActionDisplay.textContent = activePlayer ? `🕯️ ${activePlayer.name.toUpperCase()} RECITING` : '🌙 WAITING';
            playerActionDisplay.style.color = 'var(--antique-gold)';
        }

        // Reset cards held list if drawing phase completes
        if (currentPhase !== 'drawing') {
            heldIndices = [];
        }

        // Cache opponents to prevent grid flickering
        const opponentsJson = JSON.stringify(opponents) + "|" + data.active_player_id;
        if (opponentsJson !== lastOpponentsJson) {
            renderOpponents(opponents, data.active_player_id);
            lastOpponentsJson = opponentsJson;
        }
        
        // Render 3D player grimoire cards
        if (me.hand) {
            const cardsJson = JSON.stringify(me.hand.cards);
            if (cardsJson !== lastCardsJson) {
                renderHand(me.hand.cards);
                lastCardsJson = cardsJson;
            }
            handRankElement.innerHTML = `<span>🔮 Hand Combo:</span> <span class="val">${me.hand.rank}</span>`;
        } else {
            if (lastCardsJson !== 'none') {
                // Deal empty grimoire layout (5 card back overlays with staggered deals)
                cardsContainer.innerHTML = Array(5).fill(0).map((_, i) => `
                    <div class="card back" style="animation-delay: ${i * 0.08}s;">
                        <div class="card-inner" style="transform: rotateY(180deg);">
                            <div class="card-front"></div>
                            <div class="card-back"></div>
                        </div>
                    </div>
                `).join('');
                lastCardsJson = 'none';
            }
            handRankElement.innerHTML = '<span>🔮 Hand Combo:</span> <span class="val">Waiting...</span>';
        }

        // Toggle action items based on game loop phases
        if (isAutoplayActive) {
            dealBtn.style.display = 'none';
            bettingActions.style.display = 'none';
            drawBtn.style.display = 'none';
            document.getElementById('bet-input-container').style.display = 'none';
        } else {
            if (currentPhase === 'waiting') {
                dealBtn.style.display = 'inline-block';
                bettingActions.style.display = 'none';
                drawBtn.style.display = 'none';
                document.getElementById('bet-input-container').style.display = 'block';
            } else if (currentPhase === 'drawing') {
                dealBtn.style.display = 'none';
                bettingActions.style.display = 'none';
                drawBtn.style.display = isMyTurn ? 'inline-block' : 'none';
                document.getElementById('bet-input-container').style.display = 'none';
            } else { // betting_1, betting_2
                dealBtn.style.display = 'none';
                bettingActions.style.display = isMyTurn ? 'inline-block' : 'none';
                drawBtn.style.display = 'none';
                document.getElementById('bet-input-container').style.display = 'block';
                
                // Re-label active call/check options in witchy style
                const callAmount = data.current_bet - me.current_bet;
                callBtn.textContent = callAmount > 0 ? `🍵 Drink Cauldron ($${callAmount})` : '🍵 Peer Cauldron (Check)';
            }
        }
    }

    function formatPhase(phase) {
        return phase.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    /**
     * Renders opponents in circular layouts with custom seating classes (seat-bot1, etc.)
     */
    function renderOpponents(opponents, activePlayerId) {
        playerSeatsContainer.innerHTML = '';
        opponents.forEach(opp => {
            const div = document.createElement('div');
            div.className = `opponent seat-${opp.id} ${opp.id === activePlayerId ? 'active' : ''}`;
            
            let cardHtml = '';
            if (opp.hand) {
                // If showdown, expose cards
                opp.hand.cards.forEach(c => {
                   cardHtml += `<div class="card-tiny suit-${c.suit.toLowerCase()}">${c.rank}${getSuitSymbol(c.suit)}</div>`;
                });
            } else if (!opp.is_folded && currentPhase !== 'waiting') {
                // Display 5 elegant runic backs for bots actively in hand
                cardHtml = '<div class="card-tiny"></div>'.repeat(5);
            }

            let actionText = opp.last_action || 'Contemplating...';
            if (opp.is_folded) {
                actionText = '🍂 Folded';
                div.style.opacity = '0.55';
            } else {
                div.style.opacity = '1';
            }

            div.innerHTML = `
                <span class="name">🔮 ${opp.name}</span>
                <div class="opponent-cards">${cardHtml}</div>
                <span class="balance">💎 $${opp.balance}</span>
                <span class="action">${actionText}</span>
            `;
            playerSeatsContainer.appendChild(div);
        });
    }

    /**
     * Renders 3D Grimoire Hand cards
     */
    function renderHand(cards) {
        cardsContainer.innerHTML = '';
        cards.forEach((cardData, index) => {
            const card = document.createElement('div');
            card.className = `card suit-${cardData.suit.toLowerCase()} ${heldIndices.includes(index) ? 'held' : ''}`;
            card.style.animationDelay = `${index * 0.08}s`; // Micro-animation dealt sequentially

            card.innerHTML = `
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-rank-top">${cardData.rank}</div>
                        <div class="card-suit-center">${getSuitSymbol(cardData.suit)}</div>
                        <div class="card-rank-bottom">${cardData.rank}</div>
                    </div>
                    <div class="card-back"></div>
                </div>
            `;

            // Toggle card selection in transmutation draw phase
            card.addEventListener('click', () => {
                if (isAutoplayActive) return; // Disable clicking during autoplay
                if (currentPhase === 'drawing') {
                    toggleHold(index, card);
                }
            });

            cardsContainer.appendChild(card);
        });
    }

    function toggleHold(index, cardElement) {
        if (heldIndices.includes(index)) {
            heldIndices = heldIndices.filter(i => i !== index);
            cardElement.classList.remove('held');
            audio.playDeal(); // Soft select snap
        } else {
            heldIndices.push(index);
            cardElement.classList.add('held');
            audio.playChimes(); // Glistening highlight chime!
        }
    }

    // --- Action bindings ---
    dealBtn.addEventListener('click', async () => {
        audio.init();
        audio.resume();
        try {
            const bet = parseInt(betAmountInput.value);
            const response = await fetch('/bet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bet })
            });
            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'The ritual ante could not be offered.');
                return;
            }
            audio.playChimes();
            updateUI(await response.json());
        } catch (error) {
            console.error('Error starting game:', error);
        }
    });

    callBtn.addEventListener('click', async () => {
        audio.playBubble();
        try {
            const response = await fetch('/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, action: 'call' })
            });
            updateUI(await response.json());
        } catch (error) {
            console.error('Error in call action:', error);
        }
    });

    raiseBtn.addEventListener('click', async () => {
        audio.playSpell();
        try {
            const amount = parseInt(betAmountInput.value);
            const response = await fetch('/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, action: 'raise', amount })
            });
            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'Could not raise');
                return;
            }
            updateUI(await response.json());
        } catch (error) {
            console.error('Error raising action:', error);
        }
    });

    foldBtn.addEventListener('click', async () => {
        audio.playBurn();
        try {
            const response = await fetch('/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, action: 'fold' })
            });
            updateUI(await response.json());
        } catch (error) {
            console.error('Error folding:', error);
        }
    });

    drawBtn.addEventListener('click', async () => {
        audio.playChimes();
        try {
            const response = await fetch('/draw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, held_indices: heldIndices })
            });
            updateUI(await response.json());
        } catch (error) {
            console.error('Error drawing cards:', error);
        }
    });

    shuffleBtn.addEventListener('click', async () => {
        audio.playChimes();
        await fetch('/shuffle', { method: 'POST' });
        alert('Grimoire shuffled!');
        fetchState();
    });

    resetBtn.addEventListener('click', async () => {
        audio.playBurn();
        if (confirm('Extinguish the ritual hearth? Progress across the entire coven session will dissolve.')) {
            await fetch('/reset', { method: 'POST' });
            fetchState();
            fetchChatMessages();
        }
    });

    function getSuitSymbol(suit) {
        switch (suit) {
            case 'Hearts': return '♥';
            case 'Diamonds': return '♦';
            case 'Clubs': return '♣';
            case 'Spades': return '♠';
            default: return '';
        }
    }


    // --- Real-Time Chat & Automated Sound Catcher ---
    const chatMessagesDiv = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');

    async function fetchChatMessages() {
        try {
            const response = await fetch('/chat/messages?limit=50');
            if (response.ok) {
                const messages = await response.json();
                renderChatMessages(messages);
            }
        } catch (error) {
            console.error('Error whispering with coven:', error);
        }
    }

    function renderChatMessages(messages) {
        const wasAtBottom = chatMessagesDiv.scrollHeight - chatMessagesDiv.scrollTop === chatMessagesDiv.clientHeight;
        chatMessagesDiv.innerHTML = '';
        
        messages.forEach(msg => {
            const div = document.createElement('div');
            div.classList.add('chat-msg');
            
            // Extract display names
            const displayName = botNameMap[msg.player_id] || msg.player_id;
            
            if (msg.player_id === 'system') {
                div.classList.add('system');
                div.textContent = msg.text;
            } else if (msg.player_id === playerId) {
                div.classList.add('me');
                div.textContent = msg.text;
            } else {
                div.classList.add('other');
                div.textContent = `${displayName}: ${msg.text}`;
            }
            
            chatMessagesDiv.appendChild(div);

            // Automated Sound FX Trigger:
            // Intercept messages logged to play exact audio synthesis dynamically!
            if (!processedMsgIds.has(msg.id)) {
                processedMsgIds.add(msg.id);
                
                // Do not sound off messages compiled before player loaded the screen
                if (isInitialChatLoadDone) {
                    if (msg.player_id === 'system') {
                        const txt = msg.text.toLowerCase();
                        if (txt.includes('folds.')) {
                            audio.playBurn();
                        } else if (txt.includes('calls.')) {
                            audio.playBubble();
                        } else if (txt.includes('raises to') || txt.includes('raises')) {
                            audio.playSpell();
                        } else if (txt.includes('checks.')) {
                            audio.playKnock();
                        } else if (txt.includes('wins ')) {
                            audio.playVictory();
                        } else if (txt.includes('started.') || txt.includes('shuffled.')) {
                            audio.playChimes();
                        } else if (txt.includes("'s turn.")) {
                            audio.playDeal(); // Soft card tick on turns
                        }
                    } else if (msg.player_id !== 'player1') {
                        // Ambient soft bubble pop whenever bots converse!
                        audio.playBubble();
                    }
                }
            }
        });

        // Toggle load gate once the historical chats populate
        isInitialChatLoadDone = true;

        if (wasAtBottom || chatMessagesDiv.scrollTop === 0) {
            chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
        }
    }

    async function sendChatMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        try {
            await fetch('/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, text: text })
            });
            chatInput.value = '';
            fetchChatMessages();
        } catch (error) {
            console.error('Error sending whisper:', error);
        }
    }

    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Synchronized Polling
    setInterval(async () => {
        await fetchChatMessages();
        await fetchState();
    }, 2000);
});
