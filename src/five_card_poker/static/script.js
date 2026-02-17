document.addEventListener('DOMContentLoaded', () => {
    const cardsContainer = document.getElementById('cards');
    const handRankElement = document.getElementById('hand-rank');
    const deckCountElement = document.getElementById('deck-count');
    const dealBtn = document.getElementById('deal-btn');
    const shuffleBtn = document.getElementById('shuffle-btn');
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    let isDealing = false;

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        // Save preference?
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // Load saved theme
    if (localStorage.getItem('theme') === 'light') {
        body.classList.remove('dark-mode');
    }

    // Shuffle
    shuffleBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/shuffle', { method: 'POST' });
            if (response.ok) {
                alert('Deck shuffled!');
                cardsContainer.innerHTML = '';
                for (let i = 0; i < 5; i++) {
                    const card = document.createElement('div');
                    card.className = 'card back';
                    cardsContainer.appendChild(card);
                }
                handRankElement.textContent = 'Hand: Waiting to Deal';
                deckCountElement.textContent = 'Cards left: 52';
            }
        } catch (error) {
            console.error('Error shuffling:', error);
        }
    });

    // Deal
    dealBtn.addEventListener('click', async () => {
        if (isDealing) return;
        isDealing = true;
        dealBtn.disabled = true;

        try {
            const response = await fetch('/play');
            const data = await response.json();
            
            renderHand(data.cards);
            handRankElement.textContent = `Hand: ${data.rank} (Score: ${data.score})`;
            deckCountElement.textContent = `Cards left: ${data.deck_count}`;
        } catch (error) {
            console.error('Error dealing:', error);
        } finally {
            isDealing = false;
            dealBtn.disabled = false;
        }
    });

    function renderHand(cards) {
        cardsContainer.innerHTML = '';
        cards.forEach((cardData, index) => {
            const card = document.createElement('div');
            card.className = `card suit-${cardData.suit.toLowerCase()}`;
            card.innerHTML = `
                <div class="card-rank">${cardData.rank}</div>
                <div class="card-suit">${getSuitSymbol(cardData.suit)}</div>
            `;
            // Stagger animation
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            cardsContainer.appendChild(card);
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
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
