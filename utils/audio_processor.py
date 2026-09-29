import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(titles)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = (
            ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
        )
    return filename

data = (download_youtube_audio("https://www.youtube.com/watch?v=Z-zYu4patP8"))

# function to convet the audio to wisper ai compatiable like 16000 hz and set channel 1 

def convert_to_wav(input_path:str)->str:
    """Convert sny Audio / video file to WAV format using pyfub"""
    output_path = os.path.join(
    os.path.dirname(input_path),
    "converted.wav")
                   
    audio= AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path,format="wav")
    return output_path
data_final=(convert_to_wav(data))


# function to create the chunking of the audio 

def chunk_audio(wav_path: str, chunk_minute:int=5)->list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms= chunk_minute*60*1000
    chunks=[]
    for i , start in enumerate(range(0,len(audio),chunk_ms)):
        chunk= audio[start:start + chunk_ms]
        chunk_path= f"{wav_path}_chunk{i}.wav"
        chunk.export(chunk_path,format="wav")
        chunks.append(chunk_path)

    return chunks

# chunk_audio(data_final)
#  this function will combine or recognise wather the given file is url so it will send to the youtube wala  functio and so onn

def process_input(source:str)->list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected Youtube URL. Downloading Audio")
        wav_path= download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV....")
        wav_path= convert_to_wav(source)

    print("chunking audio...")
    chunks= chunk_audio(wav_path)
    print(f"Audio ready -{len(chunks)} chunk(s) created.")
    return chunks


