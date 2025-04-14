// API Configuration
const API_URL = 'http://localhost:8080';

// DOM Elements
const aiAssistant = document.getElementById('ai-assistant');
const userInput = document.getElementById('user-input');
const askButton = document.getElementById('ask-button');
const clearButton = document.getElementById('clear-button');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const searchResults = document.getElementById('search-results');
const forumsList = document.getElementById('forums-list');
const threadsList = document.getElementById('threads-list');
const threadContent = document.getElementById('thread-content');
const loadingIndicator = document.getElementById('loading-indicator');
const chatHistory = document.getElementById('chat-history');
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const userProfileElement = document.getElementById('user-profile');
const mainContent = document.getElementById('main-content');
const loginMessage = document.getElementById('login-message');

// Debug logging for element initialization
console.log('Initializing elements...');
console.log('askButton:', askButton);
console.log('userInput:', userInput);

// Auth state
let authToken = localStorage.getItem('authToken') || null;
let currentUser = null;

// Session data
let sessionId = localStorage.getItem('chatSessionId') || null;
let chatMessages = [];

// Event Listeners
if (askButton) {
    console.log('Setting up ask button event listener');
    askButton.addEventListener('click', () => {
        console.log('Ask button clicked');
        askQuestion();
    });
} else {
    console.error('Ask button not found!');
}

if (userInput) {
    console.log('Setting up user input event listener');
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            console.log('Enter key pressed in user input');
            askQuestion();
        }
    });
} else {
    console.error('User input not found!');
}

if (clearButton) clearButton.addEventListener('click', clearChat);
if (searchButton) searchButton.addEventListener('click', performSearch);
if (searchInput) searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    performSearch();
  }
});
if (loginButton) loginButton.addEventListener('click', redirectToLogin);
if (logoutButton) logoutButton.addEventListener('click', logout);

// Initialize the app
function init() {
  // Show content
  if (mainContent) mainContent.style.display = 'block';
  if (loginMessage) loginMessage.style.display = 'none';
  
  // Load forums
  loadForums();
  
  // Check for existing session
  if (sessionId) {
    loadChatHistory();
  }
  
  // Focus the input field
  if (userInput) userInput.focus();
}

// Check if user is authenticated
function checkAuth() {
  return new Promise((resolve, reject) => {
    if (!authToken) {
      reject();
      return;
    }
    
    // Fetch user profile
    fetch(`${API_URL}/user/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Unauthorized');
      }
      return response.json();
    })
    .then(data => {
      // Store user data
      currentUser = data;
      
      // Update UI with user info
      updateUserProfileUI();
      
      resolve();
    })
    .catch(() => {
      // Clear invalid token
      authToken = null;
      localStorage.removeItem('authToken');
      reject();
    });
  });
}

// Update UI with user profile info
function updateUserProfileUI() {
  if (!userProfileElement || !currentUser) return;
  
  userProfileElement.innerHTML = '';
  
  const userImg = document.createElement('img');
  userImg.src = currentUser.picture || 'https://via.placeholder.com/32';
  userImg.alt = currentUser.name;
  userImg.className = 'user-avatar';
  
  const userName = document.createElement('span');
  userName.textContent = currentUser.name;
  userName.className = 'user-name';
  
  userProfileElement.appendChild(userImg);
  userProfileElement.appendChild(userName);
  userProfileElement.style.display = 'flex';
}

// Redirect to login
function redirectToLogin() {
  window.location.href = `${API_URL}/login`;
}

// Logout
function logout() {
  // Clear auth data
  authToken = null;
  currentUser = null;
  localStorage.removeItem('authToken');
  
  // Redirect to API logout
  fetch(`${API_URL}/logout`)
    .finally(() => {
      // Reload page
      window.location.reload();
    });
}

// Load chat history from server
function loadChatHistory() {
  if (!sessionId) return;
  
  fetch(`${API_URL}/chat_history?session_id=${sessionId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load chat history');
      }
      return response.json();
    })
    .then(data => {
      chatMessages = data.history || [];
      displayChatHistory();
    })
    .catch(error => {
      console.error('Error loading chat history:', error);
    });
}

// Display chat history in the UI
function displayChatHistory() {
  if (!chatHistory) return;
  
  chatHistory.innerHTML = '';
  
  chatMessages.forEach(message => {
    const messageElement = document.createElement('div');
    messageElement.className = message.role === 'user' ? 'user-message' : 'assistant-message';
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    contentElement.textContent = message.content;
    
    messageElement.appendChild(contentElement);
    chatHistory.appendChild(messageElement);
  });
  
  // Scroll to bottom
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Ask a question to the AI
function askQuestion() {
    console.log('askQuestion function called');
    if (!userInput) {
        console.error('userInput is not defined');
        return;
    }
    
    const question = userInput.value.trim();
    console.log('Question:', question);
    if (question === '') {
        console.log('Empty question, returning');
        return;
    }
    
    // Show loading indicator
    if (loadingIndicator) {
        console.log('Showing loading indicator');
        loadingIndicator.style.display = 'block';
    }
    
    // Add user message to UI immediately
    addMessageToUI('user', question);
    
    // Clear input
    userInput.value = '';
    
    console.log('Making API request to /ask');
    // Send question to API
    fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: question,
            session_id: sessionId
        })
    })
    .then(response => {
        console.log('Received response:', response);
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        // Store session ID if returned
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('chatSessionId', sessionId);
        }
        
        // Add AI response to UI
        addMessageToUI('assistant', data.answer);
        
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error in askQuestion:', error);
        addMessageToUI('assistant', 'Sorry, there was an error processing your request.');
        
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    });
}

// Add message to UI
function addMessageToUI(role, content) {
  if (!chatHistory) return;
  
  const messageElement = document.createElement('div');
  messageElement.className = role === 'user' ? 'user-message' : 'assistant-message';
  
  const contentElement = document.createElement('div');
  contentElement.className = 'message-content';
  contentElement.textContent = content;
  
  messageElement.appendChild(contentElement);
  chatHistory.appendChild(messageElement);
  
  // Scroll to bottom
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Clear chat history
function clearChat() {
  if (!sessionId) return;
  
  fetch(`${API_URL}/clear_chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to clear chat');
    }
    return response.json();
  })
  .then(data => {
    if (chatHistory) chatHistory.innerHTML = '';
    chatMessages = [];
  })
  .catch(error => {
    console.error('Error clearing chat:', error);
  });
}

// Perform search
function performSearch() {
  if (!searchInput) return;
  
  const query = searchInput.value.trim();
  if (query === '') return;
  
  // Show loading indicator
  if (loadingIndicator) loadingIndicator.style.display = 'block';
  
  // Clear previous results
  if (searchResults) searchResults.innerHTML = '';
  
  fetch(`${API_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      top_k: 5
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to search');
    }
    return response.json();
  })
  .then(data => {
    if (!searchResults) return;
    
    if (data.results && data.results.length > 0) {
      const resultsHeader = document.createElement('h3');
      resultsHeader.textContent = 'Search Results';
      searchResults.appendChild(resultsHeader);
      
      data.results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        
        const source = document.createElement('div');
        source.className = 'result-source';
        source.textContent = `Source: ${result.source}`;
        
        const content = document.createElement('div');
        content.className = 'result-content';
        content.textContent = result.content.substring(0, 300) + (result.content.length > 300 ? '...' : '');
        
        resultItem.appendChild(source);
        resultItem.appendChild(content);
        searchResults.appendChild(resultItem);
      });
    } else {
      searchResults.textContent = 'No results found.';
    }
    
    // Hide loading indicator
    if (loadingIndicator) loadingIndicator.style.display = 'none';
  })
  .catch(error => {
    console.error('Error:', error);
    if (searchResults) searchResults.textContent = 'Error performing search.';
    
    // Hide loading indicator
    if (loadingIndicator) loadingIndicator.style.display = 'none';
  });
}

// Load forums
function loadForums() {
  if (!forumsList) return;
  
  fetch(`${API_URL}/forums`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load forums');
      }
      return response.json();
    })
    .then(data => {
      forumsList.innerHTML = '';
      
      if (data.forums && data.forums.length > 0) {
        data.forums.forEach(forum => {
          const forumItem = document.createElement('div');
          forumItem.className = 'forum-item';
          forumItem.textContent = forum.name;
          forumItem.onclick = () => loadThreads(forum.id);
          forumsList.appendChild(forumItem);
        });
      } else {
        forumsList.textContent = 'No forums available.';
      }
    })
    .catch(error => {
      console.error('Error loading forums:', error);
      forumsList.textContent = 'Error loading forums.';
    });
}

// Load threads for a forum
function loadThreads(forumId) {
  if (!threadsList) return;
  
  // Clear previous content
  threadsList.innerHTML = '';
  if (threadContent) threadContent.innerHTML = '';
  
  fetch(`${API_URL}/forum-threads/${forumId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load threads');
      }
      return response.json();
    })
    .then(data => {
      if (data.threads && data.threads.length > 0) {
        const forumHeader = document.createElement('h3');
        forumHeader.textContent = data.forum_name;
        threadsList.appendChild(forumHeader);
        
        data.threads.forEach(thread => {
          const threadItem = document.createElement('div');
          threadItem.className = 'thread-item';
          
          const title = document.createElement('div');
          title.className = 'thread-title';
          title.textContent = thread.title;
          
          const author = document.createElement('div');
          author.className = 'thread-author';
          author.textContent = `By ${thread.author}`;
          
          threadItem.appendChild(title);
          threadItem.appendChild(author);
          threadItem.onclick = () => displayThread(thread);
          
          threadsList.appendChild(threadItem);
        });
      } else {
        threadsList.textContent = 'No threads available in this forum.';
      }
    })
    .catch(error => {
      console.error('Error loading threads:', error);
      threadsList.textContent = 'Error loading threads.';
    });
}

// Display thread content
function displayThread(thread) {
  if (!threadContent) return;
  
  threadContent.innerHTML = '';
  
  const title = document.createElement('h2');
  title.textContent = thread.title;
  
  const author = document.createElement('div');
  author.className = 'thread-author';
  author.textContent = `Posted by ${thread.author}`;
  
  const date = document.createElement('div');
  date.className = 'thread-date';
  date.textContent = `Date: ${thread.date}`;
  
  const content = document.createElement('div');
  content.className = 'thread-content-text';
  content.textContent = thread.preview;
  
  threadContent.appendChild(title);
  threadContent.appendChild(author);
  threadContent.appendChild(date);
  threadContent.appendChild(content);
}

// Initialize app
document.addEventListener('DOMContentLoaded', init); 