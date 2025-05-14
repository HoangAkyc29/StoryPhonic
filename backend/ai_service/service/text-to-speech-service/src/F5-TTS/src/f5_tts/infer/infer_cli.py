import argparse
import codecs
import os
import re
import random
from datetime import datetime
from importlib.resources import files
from pathlib import Path

import numpy as np
import soundfile as sf
import tomli
from cached_path import cached_path
from omegaconf import OmegaConf

from f5_tts.infer.utils_infer import (
    mel_spec_type,
    target_rms,
    cross_fade_duration,
    nfe_step,
    cfg_strength,
    sway_sampling_coef,
    speed,
    fix_duration,
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    remove_silence_for_generated_wav,
)
from f5_tts.model import DiT, UNetT


# parser = argparse.ArgumentParser(
#     prog="python3 infer-cli.py",
#     description="Commandline interface for E2/F5 TTS with Advanced Batch Processing.",
#     epilog="Specify options above to override one or more settings from config.",
# )
# parser.add_argument(
#     "-c",
#     "--config",
#     type=str,
#     default=os.path.join(files("f5_tts").joinpath("infer/examples/basic"), "basic.toml"),
#     help="The configuration file, default see infer/examples/basic/basic.toml",
# )


# Note. Not to provide default value here in order to read default from config file

# parser.add_argument(
#     "-m",
#     "--model",
#     type=str,
#     help="The model name: F5-TTS | E2-TTS",
# )
# parser.add_argument(
#     "-mc",
#     "--model_cfg",
#     type=str,
#     help="The path to F5-TTS model config file .yaml",
# )
# parser.add_argument(
#     "-p",
#     "--ckpt_file",
#     type=str,
#     help="The path to model checkpoint .pt, leave blank to use default",
# )
# parser.add_argument(
#     "-v",
#     "--vocab_file",
#     type=str,
#     help="The path to vocab file .txt, leave blank to use default",
# )
# parser.add_argument(
#     "-r",
#     "--ref_audio",
#     type=str,
#     help="The reference audio file.",
# )
# parser.add_argument(
#     "-s",
#     "--ref_text",
#     type=str,
#     help="The transcript/subtitle for the reference audio",
# )
# parser.add_argument(
#     "-t",
#     "--gen_text",
#     type=str,
#     help="The text to make model synthesize a speech",
# )
# parser.add_argument(
#     "-f",
#     "--gen_file",
#     type=str,
#     help="The file with text to generate, will ignore --gen_text",
# )
# parser.add_argument(
#     "-o",
#     "--output_dir",
#     type=str,
#     help="The path to output folder",
# )
# parser.add_argument(
#     "-w",
#     "--output_file",
#     type=str,
#     help="The name of output file",
# )
# parser.add_argument(
#     "--save_chunk",
#     action="store_true",
#     help="To save each audio chunks during inference",
# )
# parser.add_argument(
#     "--remove_silence",
#     action="store_true",
#     help="To remove long silence found in ouput",
# )
# parser.add_argument(
#     "--load_vocoder_from_local",
#     action="store_true",
#     help="To load vocoder from local dir, default to ../checkpoints/vocos-mel-24khz",
# )
# parser.add_argument(
#     "--vocoder_name",
#     type=str,
#     choices=["vocos", "bigvgan"],
#     help=f"Used vocoder name: vocos | bigvgan, default {mel_spec_type}",
# )
# parser.add_argument(
#     "--target_rms",
#     type=float,
#     help=f"Target output speech loudness normalization value, default {target_rms}",
# )
# parser.add_argument(
#     "--cross_fade_duration",
#     type=float,
#     help=f"Duration of cross-fade between audio segments in seconds, default {cross_fade_duration}",
# )
# parser.add_argument(
#     "--nfe_step",
#     type=int,
#     help=f"The number of function evaluation (denoising steps), default {nfe_step}",
# )
# parser.add_argument(
#     "--cfg_strength",
#     type=float,
#     help=f"Classifier-free guidance strength, default {cfg_strength}",
# )
# parser.add_argument(
#     "--sway_sampling_coef",
#     type=float,
#     help=f"Sway Sampling coefficient, default {sway_sampling_coef}",
# )
# parser.add_argument(
#     "--speed",
#     type=float,
#     help=f"The speed of the generated audio, default {speed}",
# )
# parser.add_argument(
#     "--fix_duration",
#     type=float,
#     help=f"Fix the total duration (ref and gen audios) in seconds, default {fix_duration}",
# )
# args = parser.parse_args()


# # config file

# config = tomli.load(open(args.config, "rb"))


# # command-line interface parameters

# model = args.model or config.get("model", "F5-TTS")
# model_cfg = args.model_cfg or config.get("model_cfg", str(files("f5_tts").joinpath("configs/F5TTS_Base_train.yaml")))
# ckpt_file = args.ckpt_file or config.get("ckpt_file", "")
# vocab_file = args.vocab_file or config.get("vocab_file", "")

# ref_audio = args.ref_audio or config.get("ref_audio", "infer/examples/basic/basic_ref_en.wav")
# ref_text = (
#     args.ref_text
#     if args.ref_text is not None
#     else config.get("ref_text", "Some call me nature, others call me mother nature.")
# )
# gen_text = args.gen_text or config.get("gen_text", "Here we generate something just for test.")
# gen_file = args.gen_file or config.get("gen_file", "")

# output_dir = args.output_dir or config.get("output_dir", "tests")
# output_file = args.output_file or config.get(
#     "output_file", f"infer_cli_{datetime.now().strftime(r'%Y%m%d_%H%M%S')}.wav"
# )

# save_chunk = args.save_chunk or config.get("save_chunk", False)
# remove_silence = args.remove_silence or config.get("remove_silence", False)
# load_vocoder_from_local = args.load_vocoder_from_local or config.get("load_vocoder_from_local", False)

# vocoder_name = args.vocoder_name or config.get("vocoder_name", mel_spec_type)
# target_rms = args.target_rms or config.get("target_rms", target_rms)
# cross_fade_duration = args.cross_fade_duration or config.get("cross_fade_duration", cross_fade_duration)
# nfe_step = args.nfe_step or config.get("nfe_step", nfe_step)
# cfg_strength = args.cfg_strength or config.get("cfg_strength", cfg_strength)
# sway_sampling_coef = args.sway_sampling_coef or config.get("sway_sampling_coef", sway_sampling_coef)
# speed = args.speed or config.get("speed", speed)
# fix_duration = args.fix_duration or config.get("fix_duration", fix_duration)


# # patches for pip pkg user
# if "infer/examples/" in ref_audio:
#     ref_audio = str(files("f5_tts").joinpath(f"{ref_audio}"))
# if "infer/examples/" in gen_file:
#     gen_file = str(files("f5_tts").joinpath(f"{gen_file}"))
# if "voices" in config:
#     for voice in config["voices"]:
#         voice_ref_audio = config["voices"][voice]["ref_audio"]
#         if "infer/examples/" in voice_ref_audio:
#             config["voices"][voice]["ref_audio"] = str(files("f5_tts").joinpath(f"{voice_ref_audio}"))


# # ignore gen_text if gen_file provided

# if gen_file:
#     gen_text = codecs.open(gen_file, "r", "utf-8").read()


# # output path

# wave_path = Path(output_dir) / output_file
# # spectrogram_path = Path(output_dir) / "infer_cli_out.png"
# if save_chunk:
#     output_chunk_dir = os.path.join(output_dir, f"{Path(output_file).stem}_chunks")
#     if not os.path.exists(output_chunk_dir):
#         os.makedirs(output_chunk_dir)


# # load vocoder

# if vocoder_name == "vocos":
#     vocoder_local_path = "../checkpoints/vocos-mel-24khz"
# elif vocoder_name == "bigvgan":
#     vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"

# vocoder = load_vocoder(vocoder_name=vocoder_name, is_local=load_vocoder_from_local, local_path=vocoder_local_path)


# # load TTS model

# if model == "F5-TTS":
#     model_cls = DiT
#     model_cfg = OmegaConf.load(model_cfg).model.arch
#     if not ckpt_file:  # path not specified, download from repo
#         if vocoder_name == "vocos":
#             repo_name = "F5-TTS"
#             exp_name = "F5TTS_Base"
#             ckpt_step = 1200000
#             ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.safetensors"))
#             # ckpt_file = f"ckpts/{exp_name}/model_{ckpt_step}.pt"  # .pt | .safetensors; local path
#         elif vocoder_name == "bigvgan":
#             repo_name = "F5-TTS"
#             exp_name = "F5TTS_Base_bigvgan"
#             ckpt_step = 1250000
#             ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.pt"))

# elif model == "E2-TTS":
#     assert args.model_cfg is None, "E2-TTS does not support custom model_cfg yet"
#     assert vocoder_name == "vocos", "E2-TTS only supports vocoder vocos yet"
#     model_cls = UNetT
#     model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4)
#     if not ckpt_file:  # path not specified, download from repo
#         repo_name = "E2-TTS"
#         exp_name = "E2TTS_Base"
#         ckpt_step = 1200000
#         ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.safetensors"))
#         # ckpt_file = f"ckpts/{exp_name}/model_{ckpt_step}.pt"  # .pt | .safetensors; local path

# print(f"Using {model}...")
# ema_model = load_model(model_cls, model_cfg, ckpt_file, mel_spec_type=vocoder_name, vocab_file=vocab_file)


# # inference process


# def main():
#     main_voice = {"ref_audio": ref_audio, "ref_text": ref_text}
#     if "voices" not in config:
#         voices = {"main": main_voice}
#     else:
#         voices = config["voices"]
#         voices["main"] = main_voice
#     for voice in voices:
#         print("Voice:", voice)
#         print("ref_audio ", voices[voice]["ref_audio"])
#         voices[voice]["ref_audio"], voices[voice]["ref_text"] = preprocess_ref_audio_text(
#             voices[voice]["ref_audio"], voices[voice]["ref_text"]
#         )
#         print("ref_audio_", voices[voice]["ref_audio"], "\n\n")

#     generated_audio_segments = []
#     reg1 = r"(?=\[\w+\])"
#     chunks = re.split(reg1, gen_text)
#     reg2 = r"\[(\w+)\]"
#     for text in chunks:
#         if not text.strip():
#             continue
#         match = re.match(reg2, text)
#         if match:
#             voice = match[1]
#         else:
#             print("No voice tag found, using main.")
#             voice = "main"
#         if voice not in voices:
#             print(f"Voice {voice} not found, using main.")
#             voice = "main"
#         text = re.sub(reg2, "", text)
#         ref_audio_ = voices[voice]["ref_audio"]
#         ref_text_ = voices[voice]["ref_text"]
#         gen_text_ = text.strip()
#         print(f"Voice: {voice}")
#         audio_segment, final_sample_rate, spectragram = infer_process(
#             ref_audio_,
#             ref_text_,
#             gen_text_,
#             ema_model,
#             vocoder,
#             mel_spec_type=vocoder_name,
#             target_rms=target_rms,
#             cross_fade_duration=cross_fade_duration,
#             nfe_step=nfe_step,
#             cfg_strength=cfg_strength,
#             sway_sampling_coef=sway_sampling_coef,
#             speed=speed,
#             fix_duration=fix_duration,
#         )
#         generated_audio_segments.append(audio_segment)

#         if save_chunk:
#             if len(gen_text_) > 200:
#                 gen_text_ = gen_text_[:200] + " ... "
#             sf.write(
#                 os.path.join(output_chunk_dir, f"{len(generated_audio_segments)-1}_{gen_text_}.wav"),
#                 audio_segment,
#                 final_sample_rate,
#             )

#     if generated_audio_segments:
#         final_wave = np.concatenate(generated_audio_segments)

#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)

#         with open(wave_path, "wb") as f:
#             sf.write(f.name, final_wave, final_sample_rate)
#             # Remove silence
#             if remove_silence:
#                 remove_silence_for_generated_wav(f.name)
#             print(f.name)


# if __name__ == "__main__":
#     main()


# Define default values (same as in the original script)
DEFAULT_CONFIG = os.path.join(files("f5_tts").joinpath("infer/examples/basic"), "basic.toml")
DEFAULT_MEL_SPEC_TYPE = mel_spec_type
DEFAULT_MODEL = "F5-TTS"
DEFAULT_OUTPUT_DIR = "tests"
DEFAULT_VOCDER_NAME = mel_spec_type
DEFAULT_TARGET_RMS = target_rms
DEFAULT_CROSS_FADE_DURATION = cross_fade_duration
DEFAULT_NFE_STEP = nfe_step
DEFAULT_CFG_STRENGTH = cfg_strength
DEFAULT_SWAY_SAMPLING_COEF = sway_sampling_coef
DEFAULT_SPEED = speed
DEFAULT_FIX_DURATION = fix_duration


def run_inference(
    model=None,
    model_cfg=None,
    ckpt_file=None,
    vocab_file=None,
    ref_audio=None,
    ref_text=None,
    gen_text=None,
    gen_file=None,
    output_dir=None,
    output_file=None,
    save_chunk=False,
    remove_silence=False,
    load_vocoder_from_local=False,
    vocoder_name=None,
    target_rms=None,
    cross_fade_duration=None,
    nfe_step=None,
    cfg_strength=None,
    sway_sampling_coef=None,
    speed=None,
    fix_duration=None,
    config_file=DEFAULT_CONFIG
):
    """
    Runs the F5-TTS inference process.
    """
    # Load config file
    config = tomli.load(open(config_file, "rb"))

    # Use provided arguments, or fall back to config file, then defaults
    model = model or config.get("model", "F5-TTS")
    model_cfg = model_cfg or config.get("model_cfg", str(files("f5_tts").joinpath("configs/F5TTS_Base_train.yaml")))
    ckpt_file = ckpt_file or config.get("ckpt_file", "")
    vocab_file = vocab_file or config.get("vocab_file", "")

    ref_audio = ref_audio or config.get("ref_audio", "infer/examples/basic/basic_ref_en.wav")
    ref_text = (
        ref_text
        if ref_text is not None
        else config.get("ref_text", "Some call me nature, others call me mother nature.")
    )
    gen_text = gen_text or config.get("gen_text", "Here we generate something just for test.")
    gen_file = gen_file or config.get("gen_file", "")

    output_dir = output_dir or config.get("output_dir", "tests")
    output_file = output_file or config.get(
        "output_file", f"infer_cli_{datetime.now().strftime(r'%Y%m%d_%H%M%S')}.wav"
    )

    save_chunk = save_chunk or config.get("save_chunk", False)
    remove_silence = remove_silence or config.get("remove_silence", False)
    load_vocoder_from_local = load_vocoder_from_local or config.get("load_vocoder_from_local", False)

    vocoder_name = vocoder_name or config.get("vocoder_name", DEFAULT_MEL_SPEC_TYPE)
    target_rms = target_rms or config.get("target_rms", DEFAULT_TARGET_RMS)
    cross_fade_duration = cross_fade_duration or config.get("cross_fade_duration", DEFAULT_CROSS_FADE_DURATION)
    nfe_step = nfe_step or config.get("nfe_step", DEFAULT_NFE_STEP)
    cfg_strength = cfg_strength or config.get("cfg_strength", DEFAULT_CFG_STRENGTH)
    sway_sampling_coef = sway_sampling_coef or config.get("sway_sampling_coef", DEFAULT_SWAY_SAMPLING_COEF)
    speed = speed or config.get("speed", DEFAULT_SPEED)
    fix_duration = fix_duration or config.get("fix_duration", DEFAULT_FIX_DURATION)

    # patches for pip pkg user
    if "infer/examples/" in ref_audio:
        ref_audio = str(files("f5_tts").joinpath(f"{ref_audio}"))
    if "infer/examples/" in gen_file:
        gen_file = str(files("f5_tts").joinpath(f"{gen_file}"))
    if "voices" in config:
        for voice in config["voices"]:
            voice_ref_audio = config["voices"][voice]["ref_audio"]
            if "infer/examples/" in voice_ref_audio:
                config["voices"][voice]["ref_audio"] = str(files("f5_tts").joinpath(f"{voice_ref_audio}"))

    # ignore gen_text if gen_file provided
    if gen_file:
        gen_text = codecs.open(gen_file, "r", "utf-8").read()

    # output path
    wave_path = Path(output_dir) / output_file
    # spectrogram_path = Path(output_dir) / "infer_cli_out.png"
    if save_chunk:
        output_chunk_dir = os.path.join(output_dir, f"{Path(output_file).stem}_chunks")
        if not os.path.exists(output_chunk_dir):
            os.makedirs(output_chunk_dir)

    # load vocoder
    if vocoder_name == "vocos":
        vocoder_local_path = "../checkpoints/vocos-mel-24khz"
    elif vocoder_name == "bigvgan":
        vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"

    vocoder = load_vocoder(vocoder_name=vocoder_name, is_local=load_vocoder_from_local, local_path=vocoder_local_path)

    # load TTS model
    if model == "F5-TTS":
        model_cls = DiT
        model_cfg = OmegaConf.load(model_cfg).model.arch
        if not ckpt_file:  # path not specified, download from repo
            if vocoder_name == "vocos":
                repo_name = "F5-TTS"
                exp_name = "F5TTS_Base"
                ckpt_step = 1200000
                ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.safetensors"))
                # ckpt_file = f"ckpts/{exp_name}/model_{ckpt_step}.pt"  # .pt | .safetensors; local path
            elif vocoder_name == "bigvgan":
                repo_name = "F5-TTS"
                exp_name = "F5TTS_Base_bigvgan"
                ckpt_step = 1250000
                ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.pt"))

    elif model == "E2-TTS":
        assert model_cfg is None, "E2-TTS does not support custom model_cfg yet"
        assert vocoder_name == "vocos", "E2-TTS only supports vocoder vocos yet"
        model_cls = UNetT
        model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4)
        if not ckpt_file:  # path not specified, download from repo
            repo_name = "E2-TTS"
            exp_name = "E2TTS_Base"
            ckpt_step = 1200000
            ckpt_file = str(cached_path(f"hf://SWivid/{repo_name}/{exp_name}/model_{ckpt_step}.safetensors"))
            # ckpt_file = f"ckpts/{exp_name}/model_{ckpt_step}.pt"  # .pt | .safetensors; local path

    print(f"Using {model}...")
    ema_model = load_model(model_cls, model_cfg, ckpt_file, mel_spec_type=vocoder_name, vocab_file=vocab_file)

    # inference process
    main_voice = {"ref_audio": ref_audio, "ref_text": ref_text}
    if "voices" not in config:
        voices = {"main": main_voice}
    else:
        voices = config["voices"]
        voices["main"] = main_voice
    for voice in voices:
        print("Voice:", voice)
        print("ref_audio ", voices[voice]["ref_audio"])
        voices[voice]["ref_audio"], voices[voice]["ref_text"] = preprocess_ref_audio_text(
            voices[voice]["ref_audio"], voices[voice]["ref_text"]
        )
        print("ref_audio_", voices[voice]["ref_audio"], "\n\n")

    generated_audio_segments = []
    reg1 = r"(?=\[\w+\])"
    chunks = re.split(reg1, gen_text)
    reg2 = r"\[(\w+)\]"
    for text in chunks:
        if not text.strip():
            continue
        match = re.match(reg2, text)
        if match:
            voice = match[1]
        else:
            print("No voice tag found, using main.")
            voice = "main"
        if voice not in voices:
            print(f"Voice {voice} not found, using main.")
            voice = "main"
        text = re.sub(reg2, "", text)
        ref_audio_ = voices[voice]["ref_audio"]
        ref_text_ = voices[voice]["ref_text"]
        gen_text_ = text.strip()
        print(f"Voice: {voice}")
        audio_segment, final_sample_rate, spectragram = infer_process(
            ref_audio_,
            ref_text_,
            gen_text_,
            ema_model,
            vocoder,
            mel_spec_type=vocoder_name,
            target_rms=target_rms,
            cross_fade_duration=cross_fade_duration,
            nfe_step=nfe_step,
            cfg_strength=cfg_strength,
            sway_sampling_coef=sway_sampling_coef,
            speed=speed,
            fix_duration=fix_duration,
        )
        generated_audio_segments.append(audio_segment)

        if save_chunk:
            if len(gen_text_) > 200:
                gen_text_ = gen_text_[:200] + " ... "
            sf.write(
                os.path.join(output_chunk_dir, f"{len(generated_audio_segments)-1}_{gen_text_}.wav"),
                audio_segment,
                final_sample_rate,
            )

    if generated_audio_segments:
        final_wave = np.concatenate(generated_audio_segments)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(wave_path, "wb") as f:
            sf.write(f.name, final_wave, final_sample_rate)
            # Remove silence
            if remove_silence:
                remove_silence_for_generated_wav(f.name)
            print(f.name)

        return str(wave_path)
    

def multi_input_1_ref_run_inference(
    gen_texts,  # List of strings to generate
    ref_audio,
    ref_text,
    output_dir,
    model=None,
    model_cfg=None,
    ckpt_file=None,
    vocab_file=None,
    output_file_prefix="infer_cli",  # Prefix for output files
    save_chunk=False,
    remove_silence=False,
    load_vocoder_from_local=False,
    vocoder_name=None,
    target_rms=None,
    cross_fade_duration=None,
    nfe_step=None,
    cfg_strength=None,
    sway_sampling_coef=None,
    speed=None,
    fix_duration=None,
    config_file=DEFAULT_CONFIG,

):
    """
    Runs F5-TTS inference with multiple input texts and a single reference audio/text pair.
    Generates multiple output files.  Avoids redundant ref audio processing.

    Args:
        gen_texts: A list of strings, each representing text to be synthesized.
        ref_audio: Path to the reference audio file.
        ref_text: The transcript of the reference audio.
        output_dir: The directory where output files will be saved.
        model (str, optional):  Model name.
        model_cfg (str, optional): Path to model config YAML.
        ckpt_file (str, optional): Path to the model checkpoint.
        vocab_file (str, optional): Path to the vocabulary file.
        output_file_prefix (str, optional):  Prefix for the output filenames.
        save_chunk (bool, optional): Whether to save intermediate audio chunks.
        remove_silence (bool, optional):  Whether to remove long silences.
        load_vocoder_from_local (bool, optional): Load vocoder locally.
        vocoder_name (str, optional): Vocoder to use ("vocos" or "bigvgan").
        ... (other parameters):  Same as in the original run_inference.
        config_file (str, optional): Path to the config file

    Returns:
       A list of paths to the generated audio files.
    """
    # --- Load config, similar to run_inference ---
    config = tomli.load(open(config_file, "rb"))

    model = model or config.get("model", DEFAULT_MODEL)
    model_cfg = model_cfg or config.get("model_cfg", str(files("f5_tts").joinpath("configs/F5TTS_Base_train.yaml")))
    ckpt_file = ckpt_file or config.get("ckpt_file", "")
    vocab_file = vocab_file or config.get("vocab_file", "")
    load_vocoder_from_local = load_vocoder_from_local or config.get("load_vocoder_from_local", False)
    vocoder_name = vocoder_name or config.get("vocoder_name", DEFAULT_VOCDER_NAME)
    target_rms = target_rms or config.get("target_rms", DEFAULT_TARGET_RMS)
    cross_fade_duration = cross_fade_duration or config.get("cross_fade_duration", DEFAULT_CROSS_FADE_DURATION)
    nfe_step = nfe_step or config.get("nfe_step", DEFAULT_NFE_STEP)
    cfg_strength = cfg_strength or config.get("cfg_strength", DEFAULT_CFG_STRENGTH)
    sway_sampling_coef = sway_sampling_coef or config.get("sway_sampling_coef", DEFAULT_SWAY_SAMPLING_COEF)
    speed = speed or config.get("speed", DEFAULT_SPEED)
    fix_duration = fix_duration or config.get("fix_duration", DEFAULT_FIX_DURATION)
    save_chunk = save_chunk or config.get("save_chunk", False)
    remove_silence = remove_silence or config.get("remove_silence", False)


    # --- Create output directory ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- Load Vocoder (once) ---
    if vocoder_name == "vocos":
        vocoder_local_path = "../checkpoints/vocos-mel-24khz"
    elif vocoder_name == "bigvgan":
        vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"
    vocoder = load_vocoder(vocoder_name=vocoder_name, is_local=load_vocoder_from_local, local_path=vocoder_local_path)

    # --- Load TTS Model (once) ---
    if model == "F5-TTS":
        model_cls = DiT
        model_cfg = OmegaConf.load(model_cfg).model.arch
        if not ckpt_file:
            if vocoder_name == "vocos":
                ckpt_file = str(cached_path(f"hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors"))
            elif vocoder_name == "bigvgan":
                ckpt_file = str(cached_path(f"hf://SWivid/F5-TTS/F5TTS_Base_bigvgan/model_1250000.pt"))

    elif model == "E2-TTS":
        assert model_cfg is None, "E2-TTS does not support custom model_cfg yet"
        assert vocoder_name == "vocos", "E2-TTS only supports vocoder vocos yet"
        model_cls = UNetT
        model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4)
        if not ckpt_file:
            ckpt_file = str(cached_path(f"hf://SWivid/E2-TTS/E2TTS_Base/model_1200000.safetensors"))

    print(f"Using {model}...")
    ema_model = load_model(model_cls, model_cfg, ckpt_file, mel_spec_type=vocoder_name, vocab_file=vocab_file)


    # --- Preprocess Reference Audio (once) ---
    ref_audio, ref_text = preprocess_ref_audio_text(ref_audio, ref_text)
    main_voice = {"ref_audio": ref_audio, "ref_text": ref_text}
    voices = {"main": main_voice}  # Keep consistent with original structure
    # --- Main Inference Loop ---
    output_paths = []
    for i, gen_text in enumerate(gen_texts):
        # --- Construct output file name ---
        output_file = f"{output_file_prefix}_{i}_{datetime.now().strftime(r'%Y%m%d_%H%M%S')}.wav"
        wave_path = os.path.join(output_dir, output_file)

        # --- Process text with voice tags (similar to original) ---
        generated_audio_segments = []
        chunks = re.split(r"(?=\[\w+\])", gen_text)  # Split by voice tag
        for text in chunks:
            if not text.strip():
                continue
            match = re.match(r"\[(\w+)\]", text)
            voice = match[1] if match else "main"
            if voice not in voices:
                print(f"Voice {voice} not found, using main.")
                voice = "main"  # Fallback to main voice

            text = re.sub(r"\[(\w+)\]", "", text) #remove voice tag
            gen_text_ = text.strip()  # Use the current chunk as gen_text

            print(f"Processing text {i+1}/{len(gen_texts)}, Voice: {voice}")

            # --- Inference (using preprocessed ref_audio) ---
            audio_segment, final_sample_rate, _ = infer_process(
                voices[voice]["ref_audio"], # Use voices dict for consistency
                voices[voice]["ref_text"],
                gen_text_,
                ema_model,
                vocoder,
                mel_spec_type=vocoder_name,
                target_rms=target_rms,
                cross_fade_duration=cross_fade_duration,
                nfe_step=nfe_step,
                cfg_strength=cfg_strength,
                sway_sampling_coef=sway_sampling_coef,
                speed=speed,
                fix_duration=fix_duration,
            )
            generated_audio_segments.append(audio_segment)

        # --- Concatenate and save ---
        if generated_audio_segments:
            final_wave = np.concatenate(generated_audio_segments)
            with open(wave_path, "wb") as f:
                sf.write(f.name, final_wave, final_sample_rate)
                if remove_silence:
                    remove_silence_for_generated_wav(f.name)
            output_paths.append(wave_path)
            print(f"Saved to {wave_path}")

    return output_paths


_loaded_model = None  # Global variable to store the loaded model
_loaded_vocoder = None # Global variable to store the loaded vocoder

def multi_input_multi_ref_run_inference(
    ref_data,
    text_data,
    output_dir,
    constant_id = "constant_id",
    model=None,
    model_cfg=None,
    ckpt_file=None,
    vocab_file=None,
    load_vocoder_from_local=False,
    vocoder_name=None,
    output_file_prefix="infer_cli",
    save_chunk=False,
    remove_silence=False,
    target_rms=None,
    cross_fade_duration=None,
    nfe_step=None,
    cfg_strength=None,
    sway_sampling_coef=None,
    speed=None,
    fix_duration=None,
    config_file=DEFAULT_CONFIG,
):
    """
    ... (docstring - same as before, but update to reflect model loading) ...
    """
    global _loaded_model
    global _loaded_vocoder
     # --- Load config ---
    config = tomli.load(open(config_file, "rb"))
    # --- Get parameters, with fallback to config and defaults ---
    model = model or config.get("model", DEFAULT_MODEL)
    model_cfg = model_cfg or config.get("model_cfg", str(files("f5_tts").joinpath("configs/F5TTS_Base_train.yaml")))
    ckpt_file = ckpt_file or config.get("ckpt_file", "")
    vocab_file = vocab_file or config.get("vocab_file", "")
    load_vocoder_from_local = load_vocoder_from_local or config.get("load_vocoder_from_local", False)
    vocoder_name = vocoder_name or config.get("vocoder_name", DEFAULT_VOCDER_NAME)
    target_rms = target_rms or config.get("target_rms", DEFAULT_TARGET_RMS)
    cross_fade_duration = cross_fade_duration or config.get("cross_fade_duration", DEFAULT_CROSS_FADE_DURATION)
    nfe_step = nfe_step or config.get("nfe_step", DEFAULT_NFE_STEP)
    cfg_strength = cfg_strength or config.get("cfg_strength", DEFAULT_CFG_STRENGTH)
    sway_sampling_coef = sway_sampling_coef or config.get("sway_sampling_coef", DEFAULT_SWAY_SAMPLING_COEF)
    speed = speed or config.get("speed", DEFAULT_SPEED)
    fix_duration = fix_duration or config.get("fix_duration", DEFAULT_FIX_DURATION)
    save_chunk = save_chunk or config.get("save_chunk", False)
    remove_silence = remove_silence or config.get("remove_silence", False)

    # --- Load Model and Vocoder (only if not already loaded) ---
    if _loaded_model is None:
        if model == "F5-TTS":
            model_cls = DiT
            model_cfg = OmegaConf.load(model_cfg).model.arch
            if not ckpt_file:
                if vocoder_name == "vocos":
                    ckpt_file = str(cached_path(f"hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors"))
                elif vocoder_name == "bigvgan":
                    ckpt_file = str(cached_path(f"hf://SWivid/F5-TTS/F5TTS_Base_bigvgan/model_1250000.pt"))
        elif model == "E2-TTS":
            assert model_cfg is None, "E2-TTS does not support custom model_cfg yet"
            assert vocoder_name == "vocos", "E2-TTS only supports vocoder vocos yet"
            model_cls = UNetT
            model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4)
            if not ckpt_file:
                ckpt_file = str(cached_path(f"hf://SWivid/E2-TTS/E2TTS_Base/model_1200000.safetensors"))

        print(f"Loading {model} model...")
        _loaded_model = load_model(model_cls, model_cfg, ckpt_file, mel_spec_type=vocoder_name, vocab_file=vocab_file)

    if _loaded_vocoder is None:
        if vocoder_name == "vocos":
            vocoder_local_path = "../checkpoints/vocos-mel-24khz"
        elif vocoder_name == "bigvgan":
            vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"
        print(f"Loading {vocoder_name} vocoder...")
        _loaded_vocoder = load_vocoder(vocoder_name=vocoder_name, is_local=load_vocoder_from_local, local_path=vocoder_local_path)
    ema_model = _loaded_model
    vocoder = _loaded_vocoder

    all_output_paths = []

    # --- First process all reference audios ---
    voices = {}
    ref_processed_data = {}
    
    for ref_item in ref_data:
        ref_name = ref_item['ref_name']
        ref_audio = ref_item['ref_audio']
        ref_text = ref_item['ref_text']
        
        print(f"Preprocessing reference audio: {ref_name}")
        ref_audio_processed, ref_text_processed = preprocess_ref_audio_text(ref_audio, ref_text)
        
        # Store processed data for each reference
        ref_processed_data[ref_name] = {
            "ref_audio": ref_audio_processed,
            "ref_text": ref_text_processed
        }
        
        # Create voice entry (main voice for each reference)
        voices[ref_name] = {
            "main": {
                "ref_audio": ref_audio_processed,
                "ref_text": ref_text_processed
            }
        }

    # --- Now process each text item ---
    for x, item in enumerate(text_data):
        for y, sentence_data in enumerate(item):
            gen_text = sentence_data['sentence']
            choosen_ref = sentence_data['emotion']
            choosen_voice_actor = sentence_data['voice_actor']
            character_in_story = sentence_data['character']
            character_true_identity = sentence_data['identity']
            gender = sentence_data['gender'].lower()
            if not gender:
                gender = "male"
            if gender == "None":
                gender = "male"
            if not choosen_voice_actor or choosen_voice_actor == "Narrator":
                choosen_ref = "mild-trust"
            else:
                choosen_ref = find_closest_ref(choosen_ref,gender,ref_processed_data)
            if choosen_ref == "mild-trust":
                choosen_ref = f"{choosen_ref}_{gender}"
                
            # Create output directory based on reference name
            ref_output_dir = output_dir
            if not os.path.exists(ref_output_dir):
                os.makedirs(ref_output_dir)
                
            # Updated output filename format with x and y indices
            output_file = f"chunk_{x}_{y}_voice-actor_{choosen_voice_actor}_char-name_{character_in_story}_true-identity_{character_true_identity}.wav"
            wave_path = os.path.join(ref_output_dir, output_file)

            generated_audio_segments = []
            chunks = re.split(r"(?=\[\w+\])", gen_text)  # Voice tag splitting
            
            for text_chunk in chunks:
                if not text_chunk.strip():
                    continue
                    
                match = re.match(r"\[(\w+)\]", text_chunk)
                voice = match[1] if match else "main"
                
                if voice not in voices[choosen_ref]:
                    print(f"Voice {voice} not found in reference {choosen_ref}, using main.")
                    voice = "main"
                    
                text_chunk = re.sub(r"\[(\w+)\]", "", text_chunk)
                gen_text_ = text_chunk.strip()

                print(f"Processing item {x}, sentence {y} with reference: {choosen_ref}, Voice: {voice}")

                audio_segment, final_sample_rate, _ = infer_process(
                    voices[choosen_ref][voice]["ref_audio"],
                    voices[choosen_ref][voice]["ref_text"],
                    gen_text_,
                    ema_model,
                    vocoder,
                    mel_spec_type=vocoder_name,
                    target_rms=target_rms,
                    cross_fade_duration=cross_fade_duration,
                    nfe_step=nfe_step,
                    cfg_strength=cfg_strength,
                    sway_sampling_coef=sway_sampling_coef,
                    speed=speed,
                    fix_duration=fix_duration,
                )
                generated_audio_segments.append(audio_segment)

            # --- Concatenate and save ---
            if generated_audio_segments:
                final_wave = np.concatenate(generated_audio_segments)
                with open(wave_path, "wb") as f:
                    sf.write(f.name, final_wave, final_sample_rate)
                    if remove_silence:
                        remove_silence_for_generated_wav(f.name)
                all_output_paths.append(wave_path)
                print(f"Saved to {wave_path}")

    return all_output_paths


def find_closest_ref(choosen_ref: str, gender: str, ref_processed_data: dict) -> str:
    """
    Tìm ref_name gần nhất với choosen_ref theo các quy tắc:
    - Bắt buộc đúng emotion
    - Ưu tiên đúng intensity > đúng gender
    - Nếu không tìm thấy phù hợp, mặc định là "mild-trust"
    
    Args:
        choosen_ref: Chuỗi có dạng {intensity}-{emotion} hoặc None
        gender: Giới tính cần so khớp
        ref_processed_data: Dữ liệu đã xử lý chứa các ref_name
        
    Returns:
        str: ref_name phù hợp nhất
    """
    # Kiểm tra choosen_ref hợp lệ
    if not choosen_ref or not isinstance(choosen_ref, str):
        return "mild-trust"
    
    # Phân tích choosen_ref
    parts = choosen_ref.split('-')
    if len(parts) != 2:
        return "mild-trust"
    
    intensity, emotion = parts
    
    # Lấy danh sách tất cả ref_name có emotion trùng khớp
    matching_emotion_refs = []
    for ref_name in ref_processed_data.keys():
        # Phân tích ref_name (có thể có dạng: {intensity}-{emotion}_{gender} hoặc {emotion}_{gender} hoặc {emotion})
        ref_parts = re.split(r'[-_]', ref_name)
        
        # Tìm emotion trong ref_name (phần tử cuối cùng hoặc áp chót nếu có gender)
        ref_emotion = ref_parts[-1] if len(ref_parts) == 1 or (len(ref_parts) > 1 and '_' not in ref_name) else ref_parts[-2]
        
        if ref_emotion.lower() == emotion.lower():
            matching_emotion_refs.append(ref_name)
    
    # Nếu không có emotion trùng khớp
    if not matching_emotion_refs:
        return "mild-trust"
    
    # Tìm ref_name phù hợp nhất theo các tiêu chí
    best_matches = []
    
    for ref_name in matching_emotion_refs:
        ref_parts = re.split(r'[-_]', ref_name)
        ref_intensity = ref_parts[0] if '-' in ref_name else None
        ref_gender = ref_parts[-1] if '_' in ref_name else None
        
        # Tính điểm phù hợp
        score = 0
        if ref_intensity :
            if ref_intensity.lower() == intensity.lower():
                score += 2  # Ưu tiên intensity cao hơn
        if ref_gender :
            if ref_gender.lower() == gender.lower():
                score += 1
        
        best_matches.append((score, ref_name))
    
    # Sắp xếp theo điểm giảm dần
    best_matches.sort(reverse=True, key=lambda x: x[0])
    
    # Lọc các match có điểm cao nhất
    max_score = best_matches[0][0]
    top_matches = [match for match in best_matches if match[0] == max_score]
    
    # Nếu có nhiều kết quả cùng điểm, chọn ngẫu nhiên
    selected_ref = random.choice(top_matches)[1]
    
    return selected_ref