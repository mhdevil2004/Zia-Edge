
from flask import Flask, request, jsonify, send_from_directory
from gpt4all import GPT4All
from flask_cors import CORS
import datetime
import qrcode
import io
import base64
import os
import time
import socket
from threading import Lock

app = Flask(__name__, static_folder='static')
CORS(app)

print("🚀 Starting Zia Edge Enterprise Server...")
print("🔒 Privacy Mode: OFFLINE AI • ENTERPRISE GRADE")
print("💼 Zoho UI : ACTIVATED")

# Get IP automatically like server.py
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "10.175.212.187"  # Fallback to your IP

SERVER_IP = get_ip()
SERVER_PORT = 8080
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
print(f"📍 Server IP: {SERVER_IP}:{SERVER_PORT}")

# Generation/runtime tuning
CPU_THREADS = max(1, (os.cpu_count() or 2) - 1)
GENERATION_TIMEOUT_SECONDS = int(os.environ.get("GENERATION_TIMEOUT_SECONDS", 500))
MAX_RESPONSE_CHARS = int(os.environ.get("MAX_RESPONSE_CHARS", 4096))
GENERATION_CONFIG = {
    "max_tokens": int(os.environ.get("MODEL_MAX_TOKENS", 256)),
    "temp": float(os.environ.get("MODEL_TEMP", 0.65)),
    "top_k": int(os.environ.get("MODEL_TOP_K", 40)),
    "top_p": float(os.environ.get("MODEL_TOP_P", 0.9)),
    "repeat_penalty": float(os.environ.get("MODEL_REPEAT_PENALTY", 1.12)),
    "repeat_last_n": 64,
    "n_batch": int(os.environ.get("MODEL_N_BATCH", 24))
}
model_lock = Lock()

# Simple model loading exactly like server.py
try:
    model = GPT4All("orca-2-7b.Q4_0.gguf", n_threads=CPU_THREADS)
    print("✅ Orca 2 7B Model Loaded Successfully!")
    print(f"🧵 Using {CPU_THREADS} CPU threads for inference")
    model_loaded = True
except Exception as e:
    print(f"❌ Model loading error: {e}")
    print("📋 Please ensure 'orca-2-7b.Q4_0.gguf' is in your models folder")
    model = None
    model_loaded = False

# Ensure static folder exists
os.makedirs('static', exist_ok=True)

def generate_qr_code(url):
    """Generate QR code exactly like server.py"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffered = io.BytesIO()   
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

# Generate QR code on startup
QR_CODE = generate_qr_code(f"{SERVER_URL}/zia-chat")
print(f"📍 Server URL: {SERVER_URL}")
print("📱 QR Code Generated - Scan with any phone camera!")


def run_model_inference(prompt: str):
    """Generate a response with timeout and length guards to keep POST fast."""
    if not model_loaded or not model:
        return "", 0.0, False, "Model is not loaded."

    tokens = []
    char_count = 0
    timed_out = False
    start_time = time.time()

    for token in model.generate(prompt, streaming=True, **GENERATION_CONFIG):
        tokens.append(token)
        char_count += len(token)

        if char_count >= MAX_RESPONSE_CHARS:
            print("✂️ Response length cap reached, truncating output.")
            break

        if (time.time() - start_time) >= GENERATION_TIMEOUT_SECONDS:
            timed_out = True
            print("⏳ Generation timeout hit, cutting response early.")
            break

    response = ''.join(tokens).strip()
    duration = time.time() - start_time

    if not response:
        response = ""

    return response, duration, timed_out, None

@app.route('/')
def home():
    """Home page with QR code"""
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zia Edge - Enterprise Offline AI</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --zoho-red: #E41E26;
                --zoho-orange: #FF6B00;
                --gradient-primary: linear-gradient(135deg, var(--zoho-red) 0%, var(--zoho-orange) 100%);
            }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-attachment: fixed;
                min-height: 100vh;
                color: #333;
                overflow-x: hidden;
            }}
            .container {{
                max-width: 1200px;
                margin: 40px auto;
                padding: 20px;
            }}
            .glass-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(40px) saturate(180%);
                border-radius: 32px;
                box-shadow: 0 20px 60px rgba(228, 30, 38, 0.15);
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .hero-section {{
                background: var(--gradient-primary);
                color: white;
                padding: 80px 60px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            .hero-title {{
                font-size: 4.5em;
                font-weight: 800;
                margin-bottom: 20px;
                background: linear-gradient(45deg, white, #FFD700, #FF6B00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .hero-subtitle {{
                font-size: 1.4em;
                opacity: 0.95;
                margin-bottom: 40px;
            }}
            .qr-section {{
                background: linear-gradient(135deg, #2196F3 0%, #9C27B0 100%);
                color: white;
                padding: 80px 60px;
                text-align: center;
            }}
            .qr-container {{
                background: white;
                padding: 40px;
                border-radius: 24px;
                display: inline-block;
                margin: 30px 0;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s ease;
            }}
            .qr-container:hover {{
                transform: scale(1.05);
            }}
            .qr-image {{
                width: 220px;
                height: 220px;
                margin: 0 auto;
                border-radius: 12px;
            }}
            .cta-button {{
                background: var(--zoho-red);
                color: white;
                padding: 22px 50px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 700;
                font-size: 1.2em;
                display: inline-block;
                margin-top: 30px;
                box-shadow: 0 10px 30px rgba(228, 30, 38, 0.4);
                transition: all 0.4s ease;
            }}
            .cta-button:hover {{
                background: #c41a22;
                transform: translateY(-5px) scale(1.05);
                box-shadow: 0 15px 40px rgba(228, 30, 38, 0.6);
            }}
            .url-display {{
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 16px;
                margin: 30px 0;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 1.2em;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }}
            .stat-card {{
                background: rgba(255,255,255,0.15);
                padding: 25px;
                border-radius: 20px;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            @media (max-width: 768px) {{
                .hero-title {{
                    font-size: 2.8em;
                }}
                .container {{
                    margin: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="glass-container">
                <div class="hero-section">
                    <div class="zia-badge" style="background: rgba(255,255,255,0.2); padding: 16px 40px; border-radius: 50px; font-size: 1.1em; font-weight: 600; display: inline-block; margin-bottom: 30px; backdrop-filter: blur(20px);">
                        🚀 ZIA EDGE - ENTERPRISE OFFLINE AI
                    </div>
                    <h1 class="hero-title">Zia Edge</h1>
                    <p class="hero-subtitle">The Ultimate 100% Offline AI Assistant for Zoho Ecosystem</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">0ms</div>
                            <div>Cloud Latency</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">100%</div>
                            <div>Data Privacy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">∞</div>
                            <div>Uptime</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">⚡</div>
                            <div>Instant Response</div>
                        </div>
                    </div>
                </div>
                
                <div class="qr-section">
                    <h2 style="margin-bottom: 20px; font-size: 3em; font-weight: 800;">Ready to Experience Offline AI?</h2>
                    <p style="font-size: 1.3em; margin-bottom: 40px; opacity: 0.95;">Scan this QR code with your phone to start chatting offline</p>
                    
                    <div class="qr-container">
                        <img src="{QR_CODE}" alt="QR Code" class="qr-image">
                    </div>
                    
                    <div class="url-display">
                        {SERVER_URL}/zia-chat
                    </div>
                    
                    <a href="/zia-chat" class="cta-button">
                        🚀 Launch Zia Edge Chat →
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/zia-chat')
def zia_chat():
    """Production-ready chat interface with loading screen like EduMate"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zia Edge - Enterprise AI Assistant</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #fff;
            min-height: 100vh;
            overflow: hidden;
        }

        /* Loading Screen */
        #loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #0a1929, #0d2434);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.8s ease-out;
        }

        .logo-container {
            position: relative;
            width: 180px;
            height: 180px;
            margin-bottom: 40px;
        }

        .logo-outer {
            position: absolute;
            width: 100%;
            height: 100%;
            border: 4px solid rgba(228, 30, 38, 0.3);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .logo-inner {
            position: absolute;
            width: 80%;
            height: 80%;
            top: 10%;
            left: 10%;
            background: linear-gradient(45deg, #E41E26, #FF6B00);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 50px rgba(228, 30, 38, 0.5);
        }

        .logo-inner i {
            font-size: 60px;
            color: white;
        }

        .loading-text {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 20px;
            letter-spacing: 2px;
            background: linear-gradient(to right, #E41E26, #FF6B00, #E41E26);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200% auto;
            animation: gradient 3s linear infinite;
        }

        .progress-container {
            width: 300px;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(to right, #E41E26, #FF6B00);
            border-radius: 10px;
            transition: width 2s ease-in-out;
        }

        .loading-subtext {
            margin-top: 20px;
            font-size: 14px;
            opacity: 0.7;
            letter-spacing: 1px;
        }

        /* Main Chat Interface */
        #chat-interface {
            display: none;
            flex-direction: column;
            height: 100vh;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            background: rgba(10, 25, 41, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .app-title {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .app-title h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(to right, #E41E26, #FF6B00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .app-title i {
            font-size: 24px;
            color: #E41E26;
        }

        .header-controls {
            display: flex;
            gap: 20px;
        }

        .header-controls button {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .header-controls button:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .chat-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        .sidebar {
            width: 300px;
            background: rgba(15, 32, 39, 0.7);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            overflow-y: auto;
        }

        .new-chat-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(to right, #E41E26, #FF6B00);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }

        .new-chat-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(228, 30, 38, 0.4);
        }

        .history-title {
            font-size: 16px;
            margin-bottom: 15px;
            opacity: 0.7;
        }

        .chat-history {
            list-style: none;
        }

        .chat-history li {
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            background: rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .chat-history li:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 25px;
        }

        .message {
            max-width: 80%;
            padding: 20px;
            border-radius: 18px;
            line-height: 1.6;
            animation: fadeIn 0.5s ease;
        }

        .user-message {
            align-self: flex-end;
            background: linear-gradient(to right, #E41E26, #FF6B00);
            border-top-right-radius: 5px;
        }

        .ai-message {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.1);
            border-top-left-radius: 5px;
            backdrop-filter: blur(10px);
        }

        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .message-header i {
            margin-right: 8px;
        }

        .input-container {
            display: flex;
            gap: 15px;
            padding: 20px;
            background: rgba(15, 32, 39, 0.7);
            border-radius: 16px;
            margin-top: 20px;
        }

        .message-input {
            flex: 1;
            padding: 18px;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.07);
            color: white;
            font-size: 16px;
            resize: none;
            min-height: 25px;
            max-height: 150px;
            transition: all 0.3s ease;
        }

        .message-input:focus {
            outline: none;
            border-color: #E41E26;
            background: rgba(255, 255, 255, 0.1);
        }

        .send-button {
            padding: 0 25px;
            border-radius: 12px;
            border: none;
            background: linear-gradient(to right, #E41E26, #FF6B00);
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .send-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(228, 30, 38, 0.4);
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px 20px;
            border-radius: 18px;
            margin-bottom: 10px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            animation: typingAnimation 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        .connection-status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
            z-index: 1000;
        }

        .status-connected {
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.5);
        }

        .status-icon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .status-connected .status-icon {
            background: #2ecc71;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes typingAnimation {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }

        @media (max-width: 900px) {
            .sidebar { width: 230px; }
            .message { max-width: 90%; }
        }

        @media (max-width: 768px) {
            .sidebar { display: none; }
            .header { padding: 15px 20px; }
            .app-title h1 { font-size: 22px; }
        }
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-screen">
        <div class="logo-container">
            <div class="logo-outer"></div>
            <div class="logo-inner">
                <i class="fas fa-bolt"></i>
            </div>
        </div>
        <div class="loading-text">Zia Edge</div>
        <div class="progress-container">
            <div class="progress-bar" id="progress-bar"></div>
        </div>
        <div class="loading-subtext">Initializing enterprise AI assistant...</div>
    </div>

    <!-- Connection Status Indicator -->
    <div class="connection-status status-connected" id="connection-status">
        <div class="status-icon"></div>
        <span>Connected</span>
    </div>

    <!-- Chat Interface -->
    <div id="chat-interface">
        <div class="header">
            <div class="app-title">
                <i class="fas fa-bolt"></i>
                <h1>Zia Edge</h1>
            </div>
            <div class="header-controls">
                <button id="theme-toggle"><i class="fas fa-sun"></i></button>
                <a href="/"><button><i class="fas fa-home"></i></button></a>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="sidebar">
                <button class="new-chat-btn" id="new-chat-btn">
                    <i class="fas fa-plus"></i> New Chat
                </button>
                <div class="history-title">RECENT CHATS</div>
                <ul class="chat-history" id="chat-history">
                    <li><i class="fas fa-message"></i> Business Analysis</li>
                    <li><i class="fas fa-message"></i> Code Generation</li>
                    <li><i class="fas fa-message"></i> Email Writing</li>
                </ul>
            </div>
            
            <div class="chat-main">
                <div class="messages-container" id="messages-container">
                    <div class="message ai-message">
                        <div class="message-header">
                            <i class="fas fa-robot"></i> Zia Edge
                        </div>
                        <div class="message-content">
                            Hello! I'm Zia Edge, your enterprise AI assistant powered by offline AI. How can I help you today?
                        </div>
                    </div>
                </div>
                
                <div class="typing-indicator" id="typing-indicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
                
                <div class="input-container">
                    <textarea class="message-input" id="message-input" placeholder="Ask anything..." rows="1"></textarea>
                    <button class="send-button" id="send-button">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let isProcessing = false;

        document.addEventListener('DOMContentLoaded', function() {
            const loadingScreen = document.getElementById('loading-screen');
            const chatInterface = document.getElementById('chat-interface');
            const progressBar = document.getElementById('progress-bar');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const messagesContainer = document.getElementById('messages-container');
            const typingIndicator = document.getElementById('typing-indicator');
            const newChatBtn = document.getElementById('new-chat-btn');
            const themeToggle = document.getElementById('theme-toggle');

            // Simulate loading progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 2;
                progressBar.style.width = `${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(interval);
                    
                    loadingScreen.style.opacity = '0';
                    
                    setTimeout(() => {
                        loadingScreen.style.display = 'none';
                        chatInterface.style.display = 'flex';
                    }, 800);
                }
            }, 40);
            
            // Auto-resize textarea
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
            
            // Send message function
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (message && !isProcessing) {
                    // Add user message to UI
                    addMessage(message, 'user');
                    
                    // Clear input
                    messageInput.value = '';
                    messageInput.style.height = 'auto';
                    
                    // Show typing indicator
                    typingIndicator.style.display = 'flex';
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    isProcessing = true;
                    
                    try {
                        // Send message to backend
                        const response = await fetch('/ask', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: message})
                        });
                        
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        
                        const data = await response.json();
                        
                        // Hide typing indicator
                        typingIndicator.style.display = 'none';
                        
                        // Add AI response to UI
                        if (data.success && data.response) {
                            addMessage(data.response, 'ai');
                        } else {
                            addMessage("Sorry, I'm having trouble processing your request. Please try again.", 'ai');
                        }
                        
                    } catch (error) {
                        console.error('Error communicating with backend:', error);
                        typingIndicator.style.display = 'none';
                        addMessage("Sorry, I'm having trouble connecting to the server. Please make sure the backend is running.", 'ai');
                    } finally {
                        isProcessing = false;
                    }
                }
            }
            
            // Add message to chat
            function addMessage(content, type) {
                const messageEl = document.createElement('div');
                messageEl.classList.add('message');
                messageEl.classList.add(type === 'user' ? 'user-message' : 'ai-message');
                
                const header = document.createElement('div');
                header.classList.add('message-header');
                header.innerHTML = type === 'user' ? '<i class="fas fa-user"></i> You' : '<i class="fas fa-robot"></i> Zia Edge';
                
                const messageContent = document.createElement('div');
                messageContent.classList.add('message-content');
                messageContent.textContent = content;
                
                messageEl.appendChild(header);
                messageEl.appendChild(messageContent);
                
                messagesContainer.appendChild(messageEl);
                
                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            messageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // New chat button
            newChatBtn.addEventListener('click', function() {
                messagesContainer.innerHTML = '';
                addMessage("Hello! I'm Zia Edge, your enterprise AI assistant powered by offline AI. How can I help you today?", 'ai');
            });
            
            // Theme toggle
            themeToggle.addEventListener('click', function() {
                document.body.classList.toggle('light-theme');
                themeToggle.innerHTML = document.body.classList.contains('light-theme') ? 
                    '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
            });

            // Auto-focus
            messageInput.focus();
        });
    </script>
</body>
</html>
    '''

@app.route('/ask', methods=['POST'])
def ask_ai():
    """Chat endpoint exactly like server.py"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"success": False, "error": "Empty message"})
        
        if not model_loaded or not model:
            return jsonify({
                "success": False,
                "error": "AI model is not loaded. Please check the model file."
            })
        
        print(f"📱 Question: {user_message}")
        
        # Simple prompt formatting for better responses
        prompt = f"User: {user_message}\nAssistant:"
        with model_lock:
            response, response_time, timed_out, model_error = run_model_inference(prompt)

        if model_error:
            raise RuntimeError(model_error)

        # Clean up response
        response = response.strip()
        if response.startswith('Assistant:'):
            response = response[10:].strip()

        if not response:
            response = "I couldn't generate a reply fast enough. Please try asking again."

        if timed_out:
            response += "\n\n[Response truncated to keep things responsive. Try asking again for more detail.]"

        print(f"🤖 Answer ({response_time:.1f}s){' [truncated]' if timed_out else ''}: {response[:100]}...")
        
        return jsonify({
            "success": True,
            "response": response,
            "response_time": f"{response_time:.1f}s",
            "timed_out": timed_out
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory('static', 'manifest.json') if os.path.exists('static/manifest.json') else jsonify({})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "server": "Zia Edge Enterprise",
        "mode": "offline",
        "ai_model": "loaded" if model_loaded else "not_loaded",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"\n🎯 SERVER READY!")
    print(f"📍 ACCESS URL: {SERVER_URL}")
    print(f"📱 QR Code Generated - Scan with phone camera!")
    print(f"💬 Chat URL: {SERVER_URL}/zia-chat")
    print(f"🤖 Model: Orca 2 7B")
    print(f"💼 Zoho UI Framework: ACTIVATED")
    print(f"🤖 AI Model Status: {'LOADED ✅' if model_loaded else 'NOT LOADED ❌'}")
    print(f"⚡ Server starting...\n")
    
    try:
        app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("⚠️  Please check if port 8080 is available")