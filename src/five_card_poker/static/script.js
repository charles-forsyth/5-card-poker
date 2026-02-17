document.addEventListener('DOMContentLoaded', () => {
    const cardsContainer = document.getElementById('cards');
    const opponentsContainer = document.getElementById('opponents');
    const handRankElement = document.getElementById('hand-rank');
    const balanceElement = document.getElementById('balance');
    const potAmountElement = document.getElementById('pot-amount');
    const phaseDisplay = document.getElementById('phase-display');
    const betAmountInput = document.getElementById('bet-amount');
    
    const dealBtn = document.getElementById('deal-btn');
    const drawBtn = document.getElementById('draw-btn');
    const bettingActions = document.getElementById('betting-actions');
    const foldBtn = document.getElementById('fold-btn');
    const callBtn = document.getElementById('call-btn');
    const raiseBtn = document.getElementById('raise-btn');
    const shuffleBtn = document.getElementById('shuffle-btn');
    const themeToggle = document.getElementById('theme-toggle');
    
    const body = document.body;

    let heldIndices = [];
    let currentPhase = 'waiting';
    let playerId = 'player1';

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // Initialize state
    fetchState();

    async function fetchState() {
        try {
            const response = await fetch(`/state?player_id=${playerId}`);
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error fetching state:', error);
        }
    }

    function updateUI(data) {
        const me = data.players.find(p => p.id === playerId);
        const opponents = data.players.filter(p => p.id !== playerId);

        balanceElement.textContent = `Balance: $${me.balance}`;
        potAmountElement.textContent = `$${data.pot}`;
        phaseDisplay.textContent = `Phase: ${formatPhase(data.phase)}`;
        currentPhase = data.phase;

        // CRITICAL BUG FIX: Reset heldIndices if not in drawing phase
        if (currentPhase !== 'drawing') {
            heldIndices = [];
        }

        renderOpponents(opponents, data.active_player_id);
        
        if (me.hand) {
            renderHand(me.hand.cards);
            handRankElement.textContent = `Hand: ${me.hand.rank}`;
        } else {
            cardsContainer.innerHTML = '<div class="card back"></div>'.repeat(5);
            handRankElement.textContent = 'Hand: Waiting...';
        }

        // Action visibility
        const isMyTurn = data.active_player_id === playerId;
        
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
            
            // Update Call button text
            const callAmount = data.current_bet - me.current_bet;
            callBtn.textContent = callAmount > 0 ? `Call $${callAmount}` : 'Check';
        }
    }

    function formatPhase(phase) {
        return phase.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    function renderOpponents(opponents, activePlayerId) {
        opponentsContainer.innerHTML = '';
        opponents.forEach(opp => {
            const div = document.createElement('div');
            div.className = `opponent ${opp.id === activePlayerId ? 'active' : ''}`;
            
            let cardHtml = '';
            if (opp.hand) {
                // If showdown, show cards
                opp.hand.cards.forEach(c => {
                   cardHtml += `<div class="card-tiny suit-${c.suit.toLowerCase()}"></div>`;
                });
            } else {
                cardHtml = '<div class="card-tiny"></div>'.repeat(5);
            }

            div.innerHTML = `
                <span class="name">${opp.name}</span>
                <div class="opponent-cards">${cardHtml}</div>
                <span class="balance">$${opp.balance}</span>
                <span class="action">${opp.last_action}</span>
            `;
            opponentsContainer.appendChild(div);
        });
    }

    function renderHand(cards) {
        cardsContainer.innerHTML = '';
        cards.forEach((cardData, index) => {
            const card = document.createElement('div');
            card.className = `card suit-${cardData.suit.toLowerCase()} ${heldIndices.includes(index) ? 'held' : ''}`;
            
            card.innerHTML = `
                <div class="card-rank">${cardData.rank}</div>
                <div class="card-suit">${getSuitSymbol(cardData.suit)}</div>
            `;

            card.addEventListener('click', () => {
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
        } else {
            heldIndices.push(index);
            cardElement.classList.add('held');
        }
    }

    // Actions
    dealBtn.addEventListener('click', async () => {
        const bet = parseInt(betAmountInput.value);
        const response = await fetch('/bet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bet })
        });
        updateUI(await response.json());
    });

    callBtn.addEventListener('click', async () => {
        const response = await fetch('/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, action: 'call' })
        });
        updateUI(await response.json());
    });

    raiseBtn.addEventListener('click', async () => {
        const amount = parseInt(betAmountInput.value);
        const response = await fetch('/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, action: 'raise', amount })
        });
        updateUI(await response.json());
    });

    foldBtn.addEventListener('click', async () => {
        const response = await fetch('/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, action: 'fold' })
        });
        updateUI(await response.json());
    });

    drawBtn.addEventListener('click', async () => {
        const response = await fetch('/draw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, held_indices: heldIndices })
        });
        updateUI(await response.json());
    });

    shuffleBtn.addEventListener('click', async () => {
        await fetch('/shuffle', { method: 'POST' });
        alert('Deck shuffled!');
        fetchState();
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
});
