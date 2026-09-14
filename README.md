# Token Probability Visualizer

A Flask web application and Jupyter notebook for visualizing LLM token probabilities with interactive hover tooltips.

![token probability](./token-probs.png)

## 🚀 Quick Start

### Live Demo (GitHub Pages)
Visit the [live demo](https://marlenezw.github.io/token-probability) to see the token probability visualization in action with sample data.

### Local Development (Full Functionality)
For live token probability analysis with OpenAI:

1. **Clone the repository**
   ```bash
   git clone https://github.com/marlenezw/token-probability.git
   cd token-probability
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set `OPENAI_API_KEY` to your OpenAI API key. This key stays on the server and is never entered in the browser.

4. **Run the Flask app**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🌟 Features

- **Interactive Visualization**: Hover over tokens to see probability distributions
- **Live API Integration**: Connect to OpenAI for real-time token probability analysis
- **Responsive Design**: Works on desktop and mobile devices
- **Demo Mode**: GitHub Pages deployment with sample data for demonstration

## 🛠️ How It Works

### Local Environment
- Full Flask backend with `/api/generate` endpoint
- Real-time API calls to OpenAI using server-side environment configuration
- Live token probability analysis
- Complete interactivity

### GitHub Pages Demo
- Static HTML/CSS/JS deployment
- Pre-loaded sample responses
- Interactive visualization with demo data
- No backend required

## 📁 Project Structure

```
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Styles
│   ├── script.js         # Original JavaScript (for local)
│   └── script-static.js  # Static version (for GitHub Pages)
├── requirements.txt      # Python dependencies
├── generate_static.py    # Static site generator
└── .github/workflows/
    └── deploy-to-pages.yml # GitHub Actions deployment
```

## 🔧 Technical Details

- **Backend**: Flask with CORS support
- **Frontend**: Vanilla JavaScript with CSS Grid/Flexbox
- **API**: OpenAI Chat Completions with logprobs enabled
- **Deployment**: Dual-mode (local Flask + static GitHub Pages)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📝 License

See LICENSE file for details.
