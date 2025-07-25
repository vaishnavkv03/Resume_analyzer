document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('resume-file');
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);

    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results-container');
    const errorDiv = document.getElementById('error');
    
    // Reset view
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        loadingDiv.classList.add('hidden');

        if (response.ok) {
            displayResults(result);
        } else {
            displayError(result.error || 'An unknown error occurred.');
        }

    } catch (error) {
        loadingDiv.classList.add('hidden');
        displayError('Failed to connect to the server. Please try again.');
    }
});

function displayResults(data) {
    const resultsDiv = document.getElementById('results-container');
    const scoreSpan = document.getElementById('score');
    const suggestionsList = document.getElementById('suggestions-list');
    const scoreCircle = document.getElementById('score-circle');

    scoreSpan.textContent = data.score;
    
    // Change score circle color based on score
    if (data.score < 50) {
        scoreCircle.style.background = 'linear-gradient(135deg, #dc3545, #c82333)'; // Red
    } else if (data.score < 80) {
        scoreCircle.style.background = 'linear-gradient(135deg, #ffc107, #e0a800)'; // Yellow
    } else {
        scoreCircle.style.background = 'linear-gradient(135deg, #28a745, #218838)'; // Green
    }
    
    suggestionsList.innerHTML = ''; // Clear previous suggestions
    if (data.suggestions.length > 0) {
        data.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = "Excellent! Your resume seems highly ATS-friendly.";
        suggestionsList.appendChild(li);
    }
    
    resultsDiv.classList.remove('hidden');
}

function displayError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}