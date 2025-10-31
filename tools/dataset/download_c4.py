#!/usr/bin/env python3
"""
Download a small subset of the allenai/c4 dataset from HuggingFace.

This script downloads a configurable subset of the C4 dataset for testing
and development purposes. It supports streaming and local caching.
"""

import argparse
import os
import sys
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import login


def setup_hf_token():
    """Setup HuggingFace token from environment variable."""
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        login(token=hf_token)
        print("✓ HuggingFace token configured")
    else:
        print("⚠ HF_TOKEN not found in environment variables")
        print("  Some datasets may require authentication")


def download_c4_subset(
    output_dir: str = "./data/c4_subset",
    num_samples: int = 1000,
    split: str = "train",
    streaming: bool = True,  # Default to streaming to avoid large downloads
    cache_dir: str = None
):
    """
    Download a subset of the C4 dataset.
    
    Args:
        output_dir: Directory to save the dataset
        num_samples: Number of samples to download
        split: Dataset split to use ('train', 'validation')
        streaming: Whether to use streaming mode
        cache_dir: Custom cache directory for HuggingFace datasets
    """
    print(f"Downloading C4 dataset subset...")
    print(f"  Split: {split}")
    print(f"  Samples: {num_samples}")
    print(f"  Output: {output_dir}")
    print(f"  Streaming: {streaming}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Always use streaming for small subsets to avoid downloading large files
        if num_samples <= 10000 or streaming:
            print("Loading dataset in streaming mode...")
            dataset = load_dataset(
                "allenai/c4",
                "en",
                split=split,
                streaming=True,
                cache_dir=cache_dir
            )
            
            # Take subset and convert to list
            print(f"Taking first {num_samples} samples...")
            subset = []
            for i, sample in enumerate(dataset):
                if i >= num_samples:
                    break
                subset.append(sample)
                if num_samples <= 100:
                    print(f"  Downloaded {i + 1}/{num_samples} samples")
                elif (i + 1) % 100 == 0:
                    print(f"  Downloaded {i + 1}/{num_samples} samples")
            
            # Convert to dataset format
            from datasets import Dataset
            subset_dataset = Dataset.from_list(subset)
            
        else:
            print("Loading dataset (full download mode)...")
            print("Warning: This will download large files. Consider using --streaming flag.")
            dataset = load_dataset(
                "allenai/c4",
                "en",
                split=f"{split}[:{num_samples}]",
                cache_dir=cache_dir
            )
            subset_dataset = dataset
        
        # Save the subset
        output_path = Path(output_dir) / f"c4_{split}_{num_samples}.jsonl"
        print(f"Saving dataset to {output_path}...")
        
        # Save as JSONL format
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in subset_dataset:
                import json
                f.write(json.dumps(sample) + '\n')
        
        print(f"✓ Successfully downloaded {len(subset_dataset)} samples")
        print(f"✓ Saved to: {output_path}")
        
        # Print sample statistics
        if len(subset_dataset) > 0:
            sample_text = subset_dataset[0]['text']
            avg_length = sum(len(sample['text']) for sample in subset_dataset) / len(subset_dataset)
            print(f"\nDataset Statistics:")
            print(f"  Total samples: {len(subset_dataset)}")
            print(f"  Average text length: {avg_length:.0f} characters")
            print(f"  Sample text preview: {sample_text[:200]}...")
        
        return output_path
        
    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Download a subset of the allenai/c4 dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./data/c4_subset",
        help="Output directory for the dataset"
    )
    
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1000,
        help="Number of samples to download"
    )
    
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to download"
    )
    
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Force streaming mode"
    )
    
    parser.add_argument(
        "--no-streaming",
        action="store_true",
        help="Force full download mode (not recommended for small subsets)"
    )
    
    parser.add_argument(
        "--cache-dir",
        type=str,
        help="Custom cache directory for HuggingFace datasets"
    )
    
    args = parser.parse_args()
    
    # Determine streaming mode
    if args.no_streaming:
        streaming_mode = False
    elif args.streaming:
        streaming_mode = True
    else:
        # Auto-determine: use streaming for small subsets
        streaming_mode = args.num_samples <= 10000
    
    # Setup HuggingFace authentication
    setup_hf_token()
    
    # Download the dataset
    download_c4_subset(
        output_dir=args.output_dir,
        num_samples=args.num_samples,
        split=args.split,
        streaming=streaming_mode,
        cache_dir=args.cache_dir
    )


if __name__ == "__main__":
    main()