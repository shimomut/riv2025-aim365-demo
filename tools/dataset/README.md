# Dataset Download Tools

This directory contains tools for downloading and preparing datasets for FSDP training.

## C4 Dataset Download

The C4 (Colossal Clean Crawled Corpus) dataset is a large text dataset commonly used for language model training.

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Download 1000 samples (default, uses streaming automatically)
python tools/dataset/download_c4.py

# Download 5000 samples (uses streaming automatically)
python tools/dataset/download_c4.py --num-samples 5000

# Download validation split
python tools/dataset/download_c4.py --split validation --num-samples 500

# Force full download mode (not recommended for small subsets)
python tools/dataset/download_c4.py --num-samples 1000 --no-streaming
```

### Installation

Install required dependencies:

```bash
# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r tools/dataset/requirements.txt
```

### Environment Setup

For datasets requiring authentication, set your HuggingFace token:

```bash
export HF_TOKEN=your_huggingface_token_here
```

For S3 upload functionality, configure AWS credentials:

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: IAM roles (recommended for EC2/EKS)
# No additional configuration needed if running on AWS with proper IAM roles
```

### Usage Options

```bash
source .venv/bin/activate
python tools/dataset/download_c4.py [OPTIONS]

Options:
  --output-dir DIR           Output directory (default: ./data/c4_subset)
  --num-samples NUM          Number of samples to download (default: 1000)
  --split SPLIT              Dataset split: train|validation (default: train)
  --streaming                Force streaming mode
  --no-streaming             Force full download mode (not recommended for small subsets)
  --cache-dir DIR            Custom HuggingFace cache directory
  --s3-path PATH             S3 path in format 's3://bucket-name/path' to upload the dataset
  --cleanup-local            Delete local file after successful S3 upload
  --no-cleanup               Keep local file even when uploading to S3 (overrides default cleanup)
  --max-lines-per-file NUM   Maximum number of lines per JSONL file (splits into multiple files if exceeded)
  --help, -h                 Show help message

Note: When --s3-path is specified, local files are automatically cleaned up unless --no-cleanup is used.

Note: Streaming mode is automatically used for ≤10,000 samples to avoid downloading large files.
```

### Output Format

The downloaded dataset is saved as JSONL (JSON Lines) format:
- Each line contains a JSON object with the sample data
- Compatible with HuggingFace datasets library
- Easy to process with standard tools

### File Splitting

When using `--max-lines-per-file`, large datasets are automatically split into multiple files:
- Files are named with part numbers: `c4_train_10000_part001.jsonl`, `c4_train_10000_part002.jsonl`, etc.
- Each file contains at most the specified number of lines
- Files are created and uploaded to S3 (if configured) in streaming fashion
- Memory usage remains constant regardless of dataset size

### Streaming Mode

The script uses true streaming processing:
- **Memory Efficient**: Processes samples one at a time, constant memory usage
- **Real-time Upload**: Files are uploaded to S3 immediately upon completion
- **Immediate Cleanup**: Local files are deleted right after S3 upload (when `--cleanup-local` is used)
- **Fault Tolerant**: Partial progress is preserved if interrupted

### Examples

**Small development dataset:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 100 --output-dir ./data/dev_set
```

**Validation dataset:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --split validation --num-samples 500
```

**Large training subset with streaming:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 50000 --streaming --output-dir ./data/c4_large
```

**Split large dataset into multiple files:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 10000 --max-lines-per-file 2500 --output-dir ./data/c4_split
# Creates: c4_train_10000_part001.jsonl (2500 lines)
#          c4_train_10000_part002.jsonl (2500 lines)
#          c4_train_10000_part003.jsonl (2500 lines)
#          c4_train_10000_part004.jsonl (2500 lines)
```

**Upload to S3 and save disk space (cleanup is automatic):**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 5000 --s3-path s3://my-training-data/datasets/c4
```

**Upload to S3 with custom path:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 1000 --s3-path s3://my-bucket/experiments/dataset-v1
```

**Upload to S3 but keep local copy:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py --num-samples 1000 --s3-path s3://my-bucket/datasets --no-cleanup
```

**Stream large dataset with file splitting and S3 upload:**
```bash
source .venv/bin/activate
python tools/dataset/download_c4.py \
  --num-samples 50000 \
  --max-lines-per-file 5000 \
  --s3-path s3://my-bucket/datasets/c4-large \
  --cleanup-local
# Streams data directly to files, uploads each file to S3 immediately, then deletes local copy
```

### Integration with Training

The downloaded dataset can be used with the FSDP training scripts:

**Single file:**
```bash
# In your training configuration
--dataset_path ./data/c4_subset/c4_train_1000.jsonl
```

**Multiple files (when using --max-lines-per-file):**
```bash
# Use glob pattern or concatenate files
cat ./data/c4_subset/c4_train_10000_part*.jsonl > ./data/c4_subset/c4_train_10000_combined.jsonl
```

**S3 files:**
```bash
# Download single file from S3
aws s3 cp s3://my-bucket/datasets/c4/c4_train_1000.jsonl ./data/

# Download multiple files from S3
aws s3 sync s3://my-bucket/datasets/c4/ ./data/c4/ --include "c4_train_10000_part*.jsonl"
```

### S3 Upload Benefits

- **Disk Space**: Automatically clean up local files after upload
- **Sharing**: Share datasets across multiple training instances
- **Durability**: S3 provides 99.999999999% (11 9's) durability
- **Cost**: Pay only for storage used, no local disk requirements

### Troubleshooting

**Module Import Issues:**
- Ensure virtual environment is activated: `source .venv/bin/activate`
- Install dependencies: `pip install -r tools/dataset/requirements.txt`
- Check Python version compatibility (Python 3.8+ recommended)

**Authentication Issues:**
- Ensure HF_TOKEN is set for gated datasets
- Check token permissions on HuggingFace

**Memory Issues:**
- Use `--streaming` for large downloads (enabled by default for ≤10,000 samples)
- Use `--max-lines-per-file` to split large datasets into smaller files
- Reduce `--num-samples` count
- Specify custom `--cache-dir` on larger storage

**Network Issues:**
- Check internet connectivity
- Verify HuggingFace Hub accessibility
- Consider using a VPN if blocked regionally

**S3 Upload Issues:**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check bucket permissions and region
- Ensure bucket exists: `aws s3 ls s3://your-bucket-name`
- Verify network connectivity to S3