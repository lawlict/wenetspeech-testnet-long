# WenetSpeech TestNet Long Dataset

This repo contains the description file and preparation script for a long-form
audio dataset derived from WenetSpeech TestNet. **7385 segments** were created by merging adjacent short segments (typically 1–30 seconds) from 124
WenetSpeech TestNet audio files into longer chunks.

## Merge Strategy

The long-form segments were produced by iteratively merging adjacent short
segments within each source audio:

1. For two consecutive segments whose gap ≤ **5 seconds**:
2. Extend each segment by a **0.1 s collar** toward the gap.
3. Run **VAD** (voice activity detection) on the remaining gap region.
4. If the detected speech in the gap is < **0.2 s** (i.e. the gap is
   essentially silence), merge the two segments into one chunk.
5. Repeat until no more merges are possible.

Parameters:

| Parameter    | Value | Meaning                                      |
|--------------|-------|----------------------------------------------|
| max_gap      | 5.0 s | Maximum gap between segments to consider     |
| collar       | 0.1 s | Extension into the gap from each side        |
| max_leak     | 0.2 s | Max non-silence allowed in the gap for merge |

## Prerequisites

- The original WenetSpeech TestNet raw audio directory, structured as:
  ```
  WenetSpeech_test/
  ├── audio/test_net/youtube/B00000/*.opus
  ├── TERMS_OF_ACCESS
  └── WenetSpeech.json
  ```
- `ffmpeg` installed

## Usage

```bash
python prepare.py \
    --src-dir /path/to/WenetSpeech_test \
    --output-dir /path/to/output \
    --num-workers 8 \
    --sample-rate 16000
```

## Output

```
output_dir/
├── wavs/           # 7385 WAV files (16kHz mono)
│   ├── TEST_NET_..._C00000.wav
│   └── ...
└── text            # 7385 lines: sid<TAB>text
```

## JSON Schema

`WenetSpeech_testnet_long.json` follows the same structure as the original
`WenetSpeech.json`, with 124 audio entries. Each segment has:

| Field       | Description                                       |
|-------------|---------------------------------------------------|
| sid         | Chunk ID (e.g. `TEST_NET_..._C00000`)             |
| begin_time  | Start time in the source audio (seconds)          |
| end_time    | End time in the source audio (seconds)            |
| text        | Concatenated transcript                           |
| src_sids    | List of original WenetSpeech segment IDs merged   |

## Citation

```bibtex
@inproceedings{zhang2022wenetspeech,
  title={WenetSpeech: A 10000+ Hours Multi-domain Mandarin Corpus for Speech Recognition},
  author={Zhang, Binbin and Lv, Hang and Guo, Pengcheng and Shao, Qijie and Yang, Chao and Xie, Lei and Xu, Xin and Bu, Hui and Chen, Xiaoyu and Zeng, Chenhen and Wu, Di and Peng, Zhendong},
  booktitle={ICASSP 2022-2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={6182--6186},
  year={2022},
  organization={IEEE}
}
```
