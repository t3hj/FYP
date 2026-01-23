# Ollama Setup Guide - 100% Free AI for Local Lens

Ollama provides completely free, unlimited AI vision analysis running locally on your machine.

## Installation Steps

### 1. Download and Install Ollama

**Windows:**
1. Go to [https://ollama.ai/download](https://ollama.ai/download)
2. Download the Windows installer
3. Run the installer
4. Ollama will start automatically in the background

**Mac/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Install the LLaVA Vision Model

Open a terminal (PowerShell on Windows) and run:

```bash
ollama pull llava
```

This downloads the LLaVA vision model (~4.7GB). It may take a few minutes depending on your internet speed.

### 3. Verify Installation

Check that Ollama is running:

```bash
ollama list
```

You should see `llava` in the list of models.

### 4. Test It

```bash
ollama run llava
```

This will start an interactive session. You can exit with `/bye`.

## Usage with Local Lens

Once Ollama is installed and running:

1. Start your Local Lens app:
   ```bash
   streamlit run app.py
   ```

2. Upload an image - the app will automatically use Ollama for AI analysis

3. You'll see: **"🤖 AI suggests category: [Category]"**

## Benefits

✅ **100% Free** - No API keys, no subscriptions, no limits
✅ **Unlimited Usage** - Analyze as many images as you want
✅ **Works Offline** - No internet needed after initial download
✅ **Privacy** - Images never leave your computer
✅ **Fast** - Local processing, no API calls
✅ **No Quotas** - Unlike Google Gemini's daily limits

## Troubleshooting

**"Ollama not detected"**
- Make sure Ollama is running (should start automatically on system boot)
- Check: `http://localhost:11434` in your browser
- Restart Ollama: `ollama serve`

**Model not found**
- Run: `ollama pull llava` again
- Verify: `ollama list`

**Slow performance**
- LLaVA runs best with a GPU
- First run may be slower (model loading)
- Consider using smaller model: `ollama pull llava:7b`

## Alternative Models

You can try different vision models:

```bash
# Smaller, faster model
ollama pull llava:7b

# Larger, more accurate model  
ollama pull llava:13b

# Other vision models
ollama pull bakllava
```

## System Requirements

- **Minimum:** 8GB RAM
- **Recommended:** 16GB RAM, GPU (NVIDIA/AMD)
- **Disk Space:** ~5GB for LLaVA model

## Support

- Ollama Docs: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- LLaVA Model: [https://ollama.ai/library/llava](https://ollama.ai/library/llava)
