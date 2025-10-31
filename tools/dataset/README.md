# Dataset Download Tools

This directory contains tools for downloading and preparing datasets for FSDP training.

## C4 Dataset Download

The C4 (Colossal Clean Crawled Corpus) dataset is a large text dataset commonly used for language model training.

### Quick Start

```bash
# Download 1000 samples (default, uses streaming automatically)
python3 tools/dataset/download_c4.py

# Download 5000 samples (uses streaming automatically)
python3 tools/dataset/download_c4.py --num-samples 5000

# Download validation split
python3 tools/dataset/download_c4.py --split validation --num-samples 500

# Force full download mode (not recommended for small subsets)
python3 tools/dataset/download_c4.py --num-samples 1000 --no-streaming
```

### Installation

Install required dependencies:

```bash
pip install -r tools/dataset/requirements.txt
```

### Environment Setup

For datasets requiring authentication, set your HuggingFace token:

```bash
export HF_TOKEN=your_huggingface_token_here
```

### Usage Options

```bash
python3 tools/dataset/download_c4.py [OPTIONS]

Options:
  --output-dir DIR      Output directory (default: ./data/c4_subset)
  --num-samples NUM     Number of samples to download (default: 1000)
  --split SPLIT         Dataset split: train|validation (default: train)
  --streaming           Force streaming mode
  --no-streaming        Force full download mode (not recommended for small subsets)
  --cache-dir DIR       Custom HuggingFace cache directory
  --help, -h            Show help message

Note: Streaming mode is automatically used for ≤10,000 samples to avoid downloading large files.
```

### Output Format

The downloaded dataset is saved as JSONL (JSON Lines) format:
- Each line contains a JSON object with the sample data
- Compatible with HuggingFace datasets library
- Easy to process with standard tools

### Examples

**Small development dataset:**
```bash
python3 tools/dataset/download_c4.py --num-samples 100 --output-dir ./data/dev_set
```

**Validation dataset:**
```bash
python3 tools/dataset/download_c4.py --split validation --num-samples 500
```

**Large training subset with streaming:**
```bash
python3 tools/dataset/download_c4.py --num-samples 50000 --streaming --output-dir ./data/c4_large
```

### Integration with Training

The downloaded dataset can be used with the FSDP training scripts by specifying the local path:

```bash
# In your training configuration
--dataset_path ./data/c4_subset/c4_train_1000.jsonl
```

### Troubleshooting

**Authentication Issues:**
- Ensure HF_TOKEN is set for gated datasets
- Check token permissions on HuggingFace

**Memory Issues:**
- Use `--streaming` for large downloads
- Reduce `--samples` count
- Specify custom `--cache-dir` on larger storage

**Network Issues:**
- Check internet connectivity
- Verify HuggingFace Hub accessibility
- Consider using a VPN if blocked regionally