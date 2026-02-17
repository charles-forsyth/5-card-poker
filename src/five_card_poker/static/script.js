document.addEventListener('DOMContentLoaded', () => {
    const cardsContainer = document.getElementById('cards');
    const handRankElement = document.getElementById('hand-rank');
    const deckCountElement = document.getElementById('deck-count');
    const balanceElement = document.getElementById('balance');
    const currentBetDisplay = document.getElementById('current-bet-display');
    const betAmountInput = document.getElementById('bet-amount');
    
    const dealBtn = document.getElementById('deal-btn');
    const drawBtn = document.getElementById('draw-btn');
    const shuffleBtn = document.getElementById('shuffle-btn');
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    let isDealing = false;
    let heldIndices = [];
    let currentPhase = 'betting';

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    if (localStorage.getItem('theme') === 'light') {
        body.classList.remove('dark-mode');
    }

    // Initialize state
    fetchState();

    async function fetchState() {
        try {
            const response = await fetch('/state');
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error fetching state:', error);
        }
    }

    function updateUI(data) {
        balanceElement.textContent = `Balance: $${data.balance}`;
        deckCountElement.textContent = `Cards left: ${data.deck_count}`;
        handRankElement.textContent = `Hand: ${data.rank}`;
        currentBetDisplay.textContent = `Current Bet: $${data.current_bet}`;
        currentPhase = data.phase;

        if (data.cards && data.cards.length > 0) {
            renderHand(data.cards);
        }

        if (currentPhase === 'drawing') {
            dealBtn.style.display = 'none';
            drawBtn.style.display = 'inline-block';
            betAmountInput.disabled = true;
        } else {
            dealBtn.style.display = 'inline-block';
            drawBtn.style.display = 'none';
            betAmountInput.disabled = false;
            heldIndices = [];
        }
    }

    // Shuffle
    shuffleBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/shuffle', { method: 'POST' });
            const data = await response.json();
            alert('Deck shuffled!');
            cardsContainer.innerHTML = '';
            for (let i = 0; i < 5; i++) {
                const card = document.createElement('div');
                card.className = 'card back';
                cardsContainer.appendChild(card);
            }
            handRankElement.textContent = 'Hand: Waiting to Deal';
            deckCountElement.textContent = `Cards left: ${data.deck_count}`;
        } catch (error) {
            console.error('Error shuffling:', error);
        }
    });

    // Deal
    dealBtn.addEventListener('click', async () => {
        if (isDealing) return;
        const bet = parseInt(betAmountInput.value);
        if (isNaN(bet) || bet <= 0) {
            alert('Please enter a valid bet amount.');
            return;
        }

        isDealing = true;
        dealBtn.disabled = true;

        try {
            const response = await fetch('/bet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bet: bet })
            });
            const data = await response.json();
            if (data.error) {
                alert(data.error);
            } else {
                heldIndices = [];
                updateUI(data);
            }
        } catch (error) {
            console.error('Error dealing:', error);
        } finally {
            isDealing = false;
            dealBtn.disabled = false;
        }
    });

    // Draw
    drawBtn.addEventListener('click', async () => {
        if (isDealing) return;
        isDealing = true;
        drawBtn.disabled = true;

        try {
            const response = await fetch('/draw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ held_indices: heldIndices })
            });
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error drawing:', error);
        } finally {
            isDealing = false;
            drawBtn.disabled = false;
        }
    });

    function renderHand(cards) {
        cardsContainer.innerHTML = '';
        cards.forEach((cardData, index) => {
            const card = document.createElement('div');
            card.className = `card suit-${cardData.suit.toLowerCase()}`;
            if (heldIndices.includes(index)) {
                card.classList.add('held');
            }
            
            card.innerHTML = `
                <div class="card-rank">${cardData.rank}</div>
                <div class="card-suit">${getSuitSymbol(cardData.suit)}</div>
            `;

            card.addEventListener('click', () => {
                if (currentPhase === 'drawing') {
                    toggleHold(index, card);
                }
            });

            // Stagger animation
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            cardsContainer.appendChild(card);
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = (heldIndices.includes(index)) ? 'translateY(-10px)' : 'translateY(0)';
            }, index * 50);
        });
    }

    function toggleHold(index, cardElement) {
        if (heldIndices.includes(index)) {
            heldIndices = heldIndices.filter(i => i !== index);
            cardElement.classList.remove('held');
            cardElement.style.transform = 'translateY(0)';
        } else {
            heldIndices.push(index);
            cardElement.classList.add('held');
            cardElement.style.transform = 'translateY(-10px)';
        }
    }

    function getSuitSymbol(suit) {
        switch (suit) {
            case 'Hearts': return '♥';
            case 'Diamonds': return '♦';
            case 'Clubs': return '♣';
            case 'Spades': return '♠';
            default: return '';
        }
    }
});
