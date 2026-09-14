// Static version for GitHub Pages deployment
let currentTokenProbs = [];

// Sample response data for demonstration
const sampleResponse = {
    text: "conference hall where all the amazing talks are happening today!",
    tokenProbs: [
        {
            "selected_token": "conference",
            "selected_prob": 0.85,
            "top_logprobs": [
                {"token": "conference", "probability": 0.85},
                {"token": "main", "probability": 0.08},
                {"token": "exhibition", "probability": 0.04},
                {"token": "speaker", "probability": 0.02},
                {"token": "keynote", "probability": 0.01}
            ]
        },
        {
            "selected_token": " hall",
            "selected_prob": 0.72,
            "top_logprobs": [
                {"token": " hall", "probability": 0.72},
                {"token": " room", "probability": 0.15},
                {"token": " center", "probability": 0.08},
                {"token": " venue", "probability": 0.03},
                {"token": " auditorium", "probability": 0.02}
            ]
        },
        {
            "selected_token": " where",
            "selected_prob": 0.91,
            "top_logprobs": [
                {"token": " where", "probability": 0.91},
                {"token": " to", "probability": 0.04},
                {"token": " and", "probability": 0.03},
                {"token": " for", "probability": 0.01},
                {"token": " with", "probability": 0.01}
            ]
        },
        {
            "selected_token": " all",
            "selected_prob": 0.67,
            "top_logprobs": [
                {"token": " all", "probability": 0.67},
                {"token": " the", "probability": 0.18},
                {"token": " we", "probability": 0.08},
                {"token": " everyone", "probability": 0.04},
                {"token": " people", "probability": 0.03}
            ]
        },
        {
            "selected_token": " the",
            "selected_prob": 0.94,
            "top_logprobs": [
                {"token": " the", "probability": 0.94},
                {"token": " those", "probability": 0.03},
                {"token": " our", "probability": 0.02},
                {"token": " these", "probability": 0.01},
                {"token": " my", "probability": 0.001}
            ]
        },
        {
            "selected_token": " amazing",
            "selected_prob": 0.56,
            "top_logprobs": [
                {"token": " amazing", "probability": 0.56},
                {"token": " great", "probability": 0.22},
                {"token": " wonderful", "probability": 0.12},
                {"token": " exciting", "probability": 0.06},
                {"token": " fantastic", "probability": 0.04}
            ]
        },
        {
            "selected_token": " talks",
            "selected_prob": 0.89,
            "top_logprobs": [
                {"token": " talks", "probability": 0.89},
                {"token": " presentations", "probability": 0.06},
                {"token": " sessions", "probability": 0.03},
                {"token": " speakers", "probability": 0.01},
                {"token": " workshops", "probability": 0.01}
            ]
        },
        {
            "selected_token": " are",
            "selected_prob": 0.78,
            "top_logprobs": [
                {"token": " are", "probability": 0.78},
                {"token": " will", "probability": 0.12},
                {"token": " have", "probability": 0.06},
                {"token": " take", "probability": 0.03},
                {"token": " begin", "probability": 0.01}
            ]
        },
        {
            "selected_token": " happening",
            "selected_prob": 0.82,
            "top_logprobs": [
                {"token": " happening", "probability": 0.82},
                {"token": " taking", "probability": 0.09},
                {"token": " being", "probability": 0.05},
                {"token": " scheduled", "probability": 0.03},
                {"token": " occurring", "probability": 0.01}
            ]
        },
        {
            "selected_token": " today",
            "selected_prob": 0.71,
            "top_logprobs": [
                {"token": " today", "probability": 0.71},
                {"token": " now", "probability": 0.15},
                {"token": " right", "probability": 0.08},
                {"token": " this", "probability": 0.04},
                {"token": " currently", "probability": 0.02}
            ]
        },
        {
            "selected_token": "!",
            "selected_prob": 0.93,
            "top_logprobs": [
                {"token": "!", "probability": 0.93},
                {"token": ".", "probability": 0.05},
                {"token": ",", "probability": 0.01},
                {"token": " and", "probability": 0.005},
                {"token": " -", "probability": 0.005}
            ]
        }
    ]
};

// Additional sample responses for demo purposes
const sampleResponses = [
    {
        prompt: "The weather today is",
        response: {
            text: " absolutely beautiful and perfect for outdoor activities!",
            tokenProbs: [
                {
                    "selected_token": " absolutely",
                    "selected_prob": 0.73,
                    "top_logprobs": [
                        {"token": " absolutely", "probability": 0.73},
                        {"token": " really", "probability": 0.12},
                        {"token": " quite", "probability": 0.08},
                        {"token": " very", "probability": 0.05},
                        {"token": " incredibly", "probability": 0.02}
                    ]
                },
                {
                    "selected_token": " beautiful",
                    "selected_prob": 0.89,
                    "top_logprobs": [
                        {"token": " beautiful", "probability": 0.89},
                        {"token": " lovely", "probability": 0.06},
                        {"token": " perfect", "probability": 0.03},
                        {"token": " wonderful", "probability": 0.015},
                        {"token": " amazing", "probability": 0.005}
                    ]
                }
            ]
        }
    },
    {
        prompt: "Machine learning is",
        response: {
            text: " revolutionizing how we solve complex problems across industries.",
            tokenProbs: [
                {
                    "selected_token": " revolutionizing",
                    "selected_prob": 0.67,
                    "top_logprobs": [
                        {"token": " revolutionizing", "probability": 0.67},
                        {"token": " transforming", "probability": 0.18},
                        {"token": " changing", "probability": 0.10},
                        {"token": " reshaping", "probability": 0.03},
                        {"token": " improving", "probability": 0.02}
                    ]
                },
                {
                    "selected_token": " how",
                    "selected_prob": 0.85,
                    "top_logprobs": [
                        {"token": " how", "probability": 0.85},
                        {"token": " the", "probability": 0.08},
                        {"token": " our", "probability": 0.04},
                        {"token": " every", "probability": 0.02},
                        {"token": " many", "probability": 0.01}
                    ]
                }
            ]
        }
    }
];

const wordDemoResponses = [
    {
        prompt: "The weather today is ",
        response: {
            text: "sunny",
            tokenProbs: [
                { selected_token: "sun", selected_prob: 0.71, top_logprobs: [{ token: "sun", probability: 0.71 }, { token: "rain", probability: 0.19 }, { token: "cloud", probability: 0.08 }] },
                { selected_token: "ny", selected_prob: 0.94, top_logprobs: [{ token: "ny", probability: 0.94 }, { token: "shine", probability: 0.04 }, { token: "day", probability: 0.01 }] }
            ]
        }
    },
    {
        prompt: "Machine learning is ",
        response: {
            text: "powerful",
            tokenProbs: [
                { selected_token: "power", selected_prob: 0.64, top_logprobs: [{ token: "power", probability: 0.64 }, { token: "transform", probability: 0.22 }, { token: "use", probability: 0.11 }] },
                { selected_token: "ful", selected_prob: 0.90, top_logprobs: [{ token: "ful", probability: 0.90 }, { token: "ly", probability: 0.06 }, { token: "ness", probability: 0.03 }] }
            ]
        }
    }
];

// Check if we're running locally or on GitHub Pages
const isLocalEnvironment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    displayResponse('o gato subiu no ', 'telhado', [
        { selected_token: 'tel', selected_prob: 0.60, top_logprobs: [
            { token: 'tel', probability: 0.60 }, { token: 'mur', probability: 0.30 }, { token: 'so', probability: 0.10 }
        ] },
        { selected_token: 'hado', selected_prob: 0.92, top_logprobs: [
            { token: 'hado', probability: 0.92 }, { token: 'has', probability: 0.05 }, { token: 'ha', probability: 0.02 }
        ] }
    ]);
    if (!isLocalEnvironment) {
        setupStaticDemo();
    }
});

function setupStaticDemo() {
    // Add demo section for GitHub Pages
    const inputSection = document.querySelector('.input-section');
    const demoSection = document.createElement('div');
    demoSection.className = 'demo-section';
    demoSection.innerHTML = `
        <div class="demo-header">
            <h3>📍 GitHub Pages Demo Mode</h3>
            <p>This is a static demonstration. For live API functionality, <a href="https://github.com/marlenezw/token-probability" target="_blank">clone the repository</a> and run locally.</p>
        </div>
        <div class="demo-buttons">
            <button class="demo-btn" onclick="loadDemoExample(0)">Weather Example</button>
            <button class="demo-btn" onclick="loadDemoExample(1)">ML Example</button>
            <button class="demo-btn" onclick="loadOriginalExample()">Original Example</button>
        </div>
    `;
    
    inputSection.parentNode.insertBefore(demoSection, inputSection);
    
    // Hide API configuration in demo mode
    const configSection = document.querySelector('.config-section');
    if (configSection) {
        configSection.style.display = 'none';
    }
}

function loadDemoExample(index) {
    const example = wordDemoResponses[index];
    const promptInput = document.getElementById('prompt-input');
    const userMessageContent = document.querySelector('.user-message .message-content .prompt-text');
    
    // Update prompt input
    promptInput.value = example.prompt;
    
    // Update user message in chat
    userMessageContent.textContent = example.prompt;
    
    // Display the response
    displayResponse(example.prompt, example.response.text, example.response.tokenProbs);
}

function loadOriginalExample() {
    const promptInput = document.getElementById('prompt-input');
    const userMessageContent = document.querySelector('.user-message .message-content .prompt-text');
    
    // Reset to original example
    promptInput.value = "o gato subiu no ";
    userMessageContent.textContent = "o gato subiu no ";
    
    displayResponse('o gato subiu no ', 'telhado', [
        { selected_token: 'tel', selected_prob: 0.60, top_logprobs: [{ token: 'tel', probability: 0.60 }, { token: 'mur', probability: 0.30 }, { token: 'so', probability: 0.10 }] },
        { selected_token: 'hado', selected_prob: 0.92, top_logprobs: [{ token: 'hado', probability: 0.92 }, { token: 'has', probability: 0.05 }, { token: 'ha', probability: 0.02 }] }
    ]);
}

let currentPrompt = '';

function formatToken(token) {
    return token.replace(/ /g, '␠').replace(/\n/g, '↵').replace(/\t/g, '⇥');
}

function displayResponse(prompt, text, tokenProbs) {
    currentPrompt = prompt;
    currentTokenProbs = tokenProbs;
    const responseElement = document.getElementById('response-text');
    responseElement.innerHTML = '';
    
    tokenProbs.forEach((tokenData, index) => {
        const tokenButton = document.createElement('button');
        tokenButton.type = 'button';
        tokenButton.className = 'token';
        tokenButton.textContent = formatToken(tokenData.selected_token);
        tokenButton.dataset.tokenIndex = index;
        
        // Add probability-based class
        const probClass = getProbabilityClass(tokenData.selected_prob);
        tokenButton.classList.add(probClass);
        tokenButton.addEventListener('click', () => selectToken(index));
        
        responseElement.appendChild(tokenButton);
    });
    selectToken(0);
}

function getProbabilityClass(probability) {
    if (probability >= 0.8) return 'prob-very-high';
    if (probability >= 0.6) return 'prob-high';
    if (probability >= 0.4) return 'prob-medium';
    if (probability >= 0.2) return 'prob-low';
    return 'prob-very-low';
}

function selectToken(tokenIndex) {
    const tokenData = currentTokenProbs[tokenIndex];
    document.getElementById('token-context').textContent = currentPrompt + currentTokenProbs.slice(0, tokenIndex).map(item => item.selected_token).join('');
    document.querySelectorAll('.token').forEach((button, index) => {
        button.classList.toggle('token-selected', index === tokenIndex);
        button.setAttribute('aria-pressed', String(index === tokenIndex));
    });
    const rows = [...tokenData.top_logprobs];
    if (!rows.some(item => item.token === tokenData.selected_token)) rows.unshift({ token: tokenData.selected_token, probability: tokenData.selected_prob });
    const tableBody = document.getElementById('probability-table-body');
    tableBody.innerHTML = '';
    rows.forEach(item => {
        const row = document.createElement('tr');
        if (item.token === tokenData.selected_token) row.className = 'selected-candidate';
        const tokenCell = document.createElement('td');
        tokenCell.textContent = `"${formatToken(item.token)}"`;
        const probabilityCell = document.createElement('td');
        probabilityCell.textContent = `${(item.probability * 100).toFixed(1)}%`;
        row.append(tokenCell, probabilityCell);
        tableBody.appendChild(row);
    });
}

// Function handles both local and GitHub Pages environments
async function generateResponse() {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const responseElement = document.getElementById('response-text');
    
    const prompt = promptInput.value;
    
    if (!prompt.trim()) {
        alert('Please enter a prompt');
        return;
    }
    
    // Check if we're in static demo mode (GitHub Pages)
    if (!isLocalEnvironment) {
        alert('This is a static demo version hosted on GitHub Pages.\n\nTo use live API functionality:\n1. Clone the repository from GitHub\n2. Run the Flask application locally\n3. Configure OPENAI_API_KEY in your .env file\n\nFor now, try the demo examples above!');
        return;
    }
    
    // Local environment - proceed with actual API call
    // Update UI for loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="loading"></span> Generating...';
    responseElement.innerHTML = 'Generating response...';
    
    // Add user message to chat
    const chatContainer = document.querySelector('.chat-container');
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.innerHTML = `
        <div class="message-content">
            <span class="prompt-text">${prompt}</span>
        </div>
    `;
    
    // Remove existing user message if any
    const existingUserMessage = chatContainer.querySelector('.user-message');
    if (existingUserMessage) {
        existingUserMessage.remove();
    }
    
    chatContainer.insertBefore(userMessage, chatContainer.firstChild);
    
    try {
        const response = await makeApiCall(prompt);
        
        displayResponse(prompt, response.text, response.tokenProbs);
        
    } catch (error) {
        responseElement.textContent = 'Error generating response. Please check the server configuration and try again.';
        console.error('Error:', error);
    } finally {
        // Reset button state
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate';
    }
}

// API call function for local environment
async function makeApiCall(prompt) {
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                top_k: 5,
                temperature: 0.0
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Allow Enter key to submit (Shift+Enter for new line)
document.getElementById('prompt-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        generateResponse();
    }
});
