import warnings
warnings.filterwarnings("ignore")
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from typing import Optional
import torchaudio
import os

class STT:
    def __init__(self, model_id: Optional[str] = "openai/whisper-tiny", device: Optional[str] = "cpu"):
        self.model_id = model_id
        self.device = device
        self.model = None
        self.processor = None
        self.torch_dtype = torch.float32
        self._load_model()
        self.pipe = self._pipeline()

    def _load_model(self):
        device = torch.device(self.device)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, 
            torch_dtype=self.torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True
        )
        self.model.to(device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def _pipeline(self):
        return pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

    def _load_recorded_audio(self, path_audio: str, input_sample_rate=48000, output_sample_rate=16000):
        # Dataset: convert recorded audio to vector
        waveform, sample_rate = torchaudio.load(path_audio)
        waveform_resampled = torchaudio.functional.resample(
            waveform, 
            orig_freq=input_sample_rate, 
            new_freq=output_sample_rate
        )  # Change sample rate to 16000 to match training.
        sample = waveform_resampled.numpy()[0]
        return sample

    def run_inference(self, path_audio: str, output_lang: str):
        sample = self._load_recorded_audio(path_audio)
        result = self.pipe(sample, generate_kwargs={"language": output_lang, "task": "transcribe"})
        return result["text"]
    
if __name__ == '__main__':
    # stt_engine = STT(model_id = "openai/whisper-tiny", device = "cpu")
    stt_engine = STT(model_id = "openai/whisper-large-v3-turbo", device = "cpu")
    path_audio = "Posdcast.wav"
    if os.path.isfile(path_audio): print("True")
    output_lang = "en"
    text = stt_engine.run_inference(path_audio, output_lang)
    print(text)