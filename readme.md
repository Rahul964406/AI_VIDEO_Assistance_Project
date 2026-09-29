# AI Video Assistant

AI Video Assistant processes YouTube videos or local audio/video files, creates a transcript, generates a meeting summary and key points, and answers questions about the transcript.

## Features

- Accepts a YouTube URL or a local media file as input
- Converts audio to mono, 16 kHz WAV and splits it into 5-minute chunks
- Uses local OpenAI Whisper for English transcription
- Uses Sarvam AI for Hinglish transcription and English translation
- Generates a meeting title, summary, action items, decisions, and open questions
- Answers questions about the transcript using retrieval-augmented generation (RAG)
- Stores Chroma vector data locally and uses Hugging Face sentence embeddings

## Current Project Status

The currently implemented workflow is command-line based (CLI). The requirements file includes packages for a Streamlit UI and PDF/TXT export, but those features do not appear to be implemented in the current Python code.

## Project Structure

```text
.
├── main.py
├── Requirments.txt
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarize.py
│   ├── transcriber.py
│   └── vector_store.py
├── utils/
│   └── audio_processor.py
└── vector_db/
```

The `downloads/` folder is created at runtime for downloaded, converted, and chunked audio files. The `vector_db/` folder stores the Chroma database.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer
- FFmpeg installed and available in the system `PATH`
- An OpenAI API key
- A Sarvam API key for `hinglish` transcription
- An internet connection for downloading YouTube audio

The Whisper and Hugging Face embedding models may be downloaded the first time they are used. OpenAI API calls may incur charges, depending on your account and usage.

## Setup: Windows PowerShell

Open a terminal in the project folder and create a virtual environment:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r Requirments.txt
```

The requirements file is currently named `Requirments.txt` (with this spelling). If you rename it to `requirements.txt`, use the new name in the install command as well.

Verify that FFmpeg is available:

```powershell
ffmpeg -version
```

If the command is not found, install FFmpeg and add its `bin` folder to the system `PATH`. The `ffmpeg-python` package is only a Python wrapper; it does not replace the FFmpeg executable.

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

# Required for Hinglish transcription
SARVAM_API_KEY=your_sarvam_api_key

# Optional settings
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

`OPENAI_API_KEY` is required for title generation, summaries, extraction, and RAG answers. `SARVAM_API_KEY` is required only for `hinglish` transcription. Do not commit API keys to a public repository.

## Run the Application

Run the application from the project root:

```powershell
python main.py
```

The program first asks for a YouTube URL or local file path, then asks for the transcription language:

- `english`: uses local Whisper transcription
- `hinglish`: uses Sarvam transcription and translation

After processing, the program prints the title, summary, action items, key decisions, and open questions. It then starts an interactive chat about the meeting transcript. Type `exit`, `quit`, or `q` to end the chat.

A Windows local file path can look like this:

```text
C:\Users\YourName\Videos\meeting.mp4
```

Supported media formats depend on the installed FFmpeg and pydub configuration.

## Processing Flow

1. `main.py` passes the input to `process_input()` in `utils/audio_processor.py`.
2. For a YouTube URL, `yt-dlp` downloads the audio. For a local path, the media file is read directly.
3. The audio is converted to mono, 16 kHz WAV and split into 5-minute chunks.
4. `core/transcriber.py` uses Whisper for `english` and Sarvam for `hinglish`. For Sarvam requests, the audio is sent in 25-second pieces.
5. `core/summarize.py` generates the meeting title and summary.
6. `core/extractor.py` extracts action items, decisions, and unresolved questions.
7. `core/vector_store.py` creates transcript embeddings and stores them in Chroma.
8. `core/rag_engine.py` retrieves relevant transcript context and generates answers to user questions.

LLM operations use `gpt-4o-mini`. Vector embeddings use the `all-MiniLM-L6-v2` model, configured to run on the CPU.

## Generated Data

- `downloads/`: downloaded audio, converted WAV files, and audio chunks
- `vector_db/`: Chroma vector database
- Whisper and Hugging Face model files: stored in the libraries' local cache

Check whether you still need generated data before deleting it. If you delete the vector database, its data will need to be created again.

## Troubleshooting

- **OpenAI authentication error:** Check that `OPENAI_API_KEY` is set correctly in `.env` and that you are running the application from the project root.
- **Sarvam authentication error:** Set `SARVAM_API_KEY` in `.env` when using `hinglish` mode.
- **FFmpeg not found:** Run `ffmpeg -version` and check the FFmpeg installation and system `PATH`.
- **Whisper or PyTorch installation issue:** Check that the virtual environment is active and that your Python version is supported. A platform-specific PyTorch installation may be required.
- **YouTube download issue:** Check your internet connection, the URL, and the installed `yt-dlp` version.
- **Slow first run:** Whisper or the embedding model may be downloading or loading for the first time.
- **Unsupported media file:** Check the input format and FFmpeg installation.

## Current Code Caveats

- `utils/audio_processor.py` contains hard-coded YouTube demo download and conversion calls at the module level. This means the demo download may run as soon as `main.py` imports the module. Before normal use, comment out or remove those top-level demo calls while keeping the functions.
- `download_youtube_audio()` uses `%(titles)s` in its output template. If download filename generation fails, check the yt-dlp title template; `%(title)s` is typically the field used for a video title.
- `core/summarize.py` joins partial summaries using `"/n/n"`. If line breaks between summaries are intended, check this value.
- `load_rag_chain()` in `core/rag_engine.py` calls `get_retriever()` without the required vector store argument. The main CLI uses `build_rag_chain()`; calling `load_rag_chain()` separately may produce an error.

## Dependencies

Python dependencies are listed in `Requirments.txt`. Some listed packages, including Streamlit, PDF export libraries, and translation utilities, are not used in the current code path and may be intended for future features.