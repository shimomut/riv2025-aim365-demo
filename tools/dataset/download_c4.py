#!/usr/bin/env python3
"""
Download a small subset of the allenai/c4 dataset from HuggingFace.

This script downloads a configurable subset of the C4 dataset for testing
and development purposes. It supports streaming and local caching.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import login
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def setup_hf_token():
    """Setup HuggingFace token from environment variable."""
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        login(token=hf_token)
        print("✓ HuggingFace token configured")
    else:
        print("⚠ HF_TOKEN not found in environment variables")
        print("  Some datasets may require authentication")


def setup_s3_client():
    """Setup S3 client and verify credentials."""
    try:
        s3_client = boto3.client('s3')
        # Test credentials by listing buckets
        s3_client.list_buckets()
        print("✓ AWS credentials configured")
        return s3_client
    except NoCredentialsError:
        print("✗ AWS credentials not found")
        print("  Configure with: aws configure")
        print("  Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return None
    except ClientError as e:
        print(f"✗ AWS credentials error: {e}")
        return None


def parse_s3_path(s3_path: str):
    """Parse S3 path into bucket and key components."""
    if not s3_path.startswith('s3://'):
        raise ValueError("S3 path must start with 's3://'")
    
    # Remove s3:// prefix and split
    path_without_prefix = s3_path[5:]  # Remove 's3://'
    parts = path_without_prefix.split('/', 1)
    
    if len(parts) < 1 or not parts[0]:
        raise ValueError("S3 path must include bucket name")
    
    bucket = parts[0]
    key_prefix = parts[1] if len(parts) > 1 else ""
    
    return bucket, key_prefix


def upload_to_s3(file_path: str, s3_bucket: str, s3_key: str, s3_client):
    """Upload file to S3 bucket."""
    try:
        print(f"Uploading to S3: s3://{s3_bucket}/{s3_key}")
        s3_client.upload_file(file_path, s3_bucket, s3_key)
        print(f"✓ Successfully uploaded to S3")
        return f"s3://{s3_bucket}/{s3_key}"
    except ClientError as e:
        print(f"✗ S3 upload failed: {e}")
        return None


def download_c4_subset(
    output_dir: str = "./data/c4_subset",
    num_samples: int = 1000,
    split: str = "train",
    streaming: bool = True,  # Default to streaming to avoid large downloads
    cache_dir: str = None,
    s3_path: str = None,
    cleanup_local: bool = False,
    max_lines_per_file: int = None
):
    """
    Download a subset of the C4 dataset.
    
    Args:
        output_dir: Directory to save the dataset (or temp dir if uploading to S3)
        num_samples: Number of samples to download
        split: Dataset split to use ('train', 'validation')
        streaming: Whether to use streaming mode
        cache_dir: Custom cache directory for HuggingFace datasets
        s3_path: S3 path in format 's3://bucket-name/path' for upload (optional)
        cleanup_local: Whether to delete local file after S3 upload
        max_lines_per_file: Maximum number of lines per JSONL file (splits into multiple files if exceeded)
    """
    print(f"Downloading C4 dataset subset...")
    print(f"  Split: {split}")
    print(f"  Samples: {num_samples}")
    print(f"  Streaming: {streaming}")
    
    # Setup S3 client if needed
    s3_client = None
    s3_bucket = None
    s3_prefix = None
    
    if s3_path:
        try:
            s3_bucket, s3_prefix = parse_s3_path(s3_path)
            s3_client = setup_s3_client()
            if not s3_client:
                print("✗ S3 upload requested but AWS credentials not available")
                sys.exit(1)
            print(f"  S3 Path: {s3_path}")
        except ValueError as e:
            print(f"✗ Invalid S3 path: {e}")
            sys.exit(1)
    
    # Use temp directory if uploading to S3 and cleanup requested
    if s3_path and cleanup_local:
        temp_dir = tempfile.mkdtemp()
        actual_output_dir = temp_dir
        print(f"  Using temp directory: {actual_output_dir}")
    else:
        actual_output_dir = output_dir
        print(f"  Output: {actual_output_dir}")
        # Create output directory
        Path(actual_output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        import json
        
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
            
            # Stream and write data directly to files
            print(f"Streaming {num_samples} samples...")
            
            # Initialize tracking variables
            output_paths = []
            s3_urls = []
            current_file = None
            current_file_path = None
            samples_in_current_file = 0
            file_idx = 0
            total_samples = 0
            text_lengths = []
            first_sample_text = None
            
            # Determine if we need multiple files
            lines_per_file = max_lines_per_file if max_lines_per_file else num_samples
            
            for i, sample in enumerate(dataset):
                if i >= num_samples:
                    break
                
                # Track first sample for statistics
                if first_sample_text is None:
                    first_sample_text = sample['text']
                text_lengths.append(len(sample['text']))
                
                # Check if we need to start a new file
                if current_file is None or (max_lines_per_file and samples_in_current_file >= max_lines_per_file):
                    # Close and upload previous file if it exists
                    if current_file is not None:
                        current_file.close()
                        
                        # Upload to S3 immediately if requested
                        if s3_path and s3_client:
                            s3_key = f"{s3_prefix}/{current_file_path.name}" if s3_prefix else current_file_path.name
                            s3_url = upload_to_s3(str(current_file_path), s3_bucket, s3_key, s3_client)
                            if s3_url:
                                s3_urls.append(s3_url)
                                
                                # Clean up local file immediately after successful upload
                                if cleanup_local:
                                    print(f"Cleaning up local file: {current_file_path}")
                                    current_file_path.unlink()
                                else:
                                    output_paths.append(str(current_file_path))
                            else:
                                # Keep local file if S3 upload failed
                                output_paths.append(str(current_file_path))
                        else:
                            # No S3 upload, keep local file
                            output_paths.append(str(current_file_path))
                    
                    # Start new file
                    file_idx += 1
                    if max_lines_per_file and num_samples > max_lines_per_file:
                        filename = f"c4_{split}_{num_samples}_part{file_idx:03d}.jsonl"
                        print(f"Starting part {file_idx} - {filename}")
                    else:
                        filename = f"c4_{split}_{num_samples}.jsonl"
                        print(f"Writing to {filename}")
                    
                    current_file_path = Path(actual_output_dir) / filename
                    current_file = open(current_file_path, 'w', encoding='utf-8')
                    samples_in_current_file = 0
                
                # Write sample to current file
                current_file.write(json.dumps(sample) + '\n')
                samples_in_current_file += 1
                total_samples += 1
                
                # Progress reporting
                if num_samples <= 100:
                    print(f"  Downloaded {total_samples}/{num_samples} samples")
                elif total_samples % 100 == 0:
                    print(f"  Downloaded {total_samples}/{num_samples} samples")
            
            # Close and upload the final file
            if current_file is not None:
                current_file.close()
                
                # Upload to S3 immediately if requested
                if s3_path and s3_client:
                    s3_key = f"{s3_prefix}/{current_file_path.name}" if s3_prefix else current_file_path.name
                    s3_url = upload_to_s3(str(current_file_path), s3_bucket, s3_key, s3_client)
                    if s3_url:
                        s3_urls.append(s3_url)
                        
                        # Clean up local file immediately after successful upload
                        if cleanup_local:
                            print(f"Cleaning up local file: {current_file_path}")
                            current_file_path.unlink()
                        else:
                            output_paths.append(str(current_file_path))
                    else:
                        # Keep local file if S3 upload failed
                        output_paths.append(str(current_file_path))
                else:
                    # No S3 upload, keep local file
                    output_paths.append(str(current_file_path))
            
            print(f"✓ Successfully streamed {total_samples} samples")
            
            # Show results based on what's available
            if s3_path and s3_urls:
                print(f"✓ Uploaded to S3: {len(s3_urls)} files")
                for s3_url in s3_urls:
                    print(f"    {s3_url}")
            
            if output_paths:
                print(f"✓ Local files: {len(output_paths)} files")
                for path in output_paths:
                    print(f"    {path}")
            
            # Print sample statistics
            if total_samples > 0:
                avg_length = sum(text_lengths) / len(text_lengths)
                print(f"\nDataset Statistics:")
                print(f"  Total samples: {total_samples}")
                print(f"  Files created: {file_idx}")
                if max_lines_per_file:
                    print(f"  Max lines per file: {max_lines_per_file}")
                print(f"  Average text length: {avg_length:.0f} characters")
                print(f"  Sample text preview: {first_sample_text[:200]}...")
            
            # Clean up temp directory if used and all files were uploaded
            if s3_path and cleanup_local and actual_output_dir != output_dir and len(s3_urls) == file_idx:
                import shutil
                shutil.rmtree(actual_output_dir)
                print(f"✓ Temp directory cleaned up")
            
            # Return S3 URLs if available, otherwise local paths
            return s3_urls if s3_urls else output_paths
            
        else:
            print("Loading dataset (full download mode)...")
            print("Warning: This will download large files. Consider using --streaming flag.")
            dataset = load_dataset(
                "allenai/c4",
                "en",
                split=f"{split}[:{num_samples}]",
                cache_dir=cache_dir
            )
            
            # For non-streaming mode, use the original approach
            if max_lines_per_file and len(dataset) > max_lines_per_file:
                # Split into multiple files
                num_files = (len(dataset) + max_lines_per_file - 1) // max_lines_per_file
                print(f"Splitting {len(dataset)} samples into {num_files} files (max {max_lines_per_file} lines per file)...")
                
                output_paths = []
                s3_urls = []
                
                for file_idx in range(num_files):
                    start_idx = file_idx * max_lines_per_file
                    end_idx = min((file_idx + 1) * max_lines_per_file, len(dataset))
                    
                    filename = f"c4_{split}_{num_samples}_part{file_idx + 1:03d}.jsonl"
                    output_path = Path(actual_output_dir) / filename
                    
                    print(f"Saving part {file_idx + 1}/{num_files} to {output_path} (samples {start_idx + 1}-{end_idx})...")
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for i in range(start_idx, end_idx):
                            f.write(json.dumps(dataset[i]) + '\n')
                    
                    # Upload to S3 immediately if requested
                    if s3_path and s3_client:
                        s3_key = f"{s3_prefix}/{filename}" if s3_prefix else filename
                        s3_url = upload_to_s3(str(output_path), s3_bucket, s3_key, s3_client)
                        if s3_url:
                            s3_urls.append(s3_url)
                            
                            # Clean up local file immediately after successful upload
                            if cleanup_local:
                                print(f"Cleaning up local file: {output_path}")
                                output_path.unlink()
                            else:
                                output_paths.append(str(output_path))
                        else:
                            # Keep local file if S3 upload failed
                            output_paths.append(str(output_path))
                    else:
                        # No S3 upload, keep local file
                        output_paths.append(str(output_path))
                
                print(f"✓ Successfully downloaded {len(dataset)} samples")
                
                # Show results based on what's available
                if s3_path and s3_urls:
                    print(f"✓ Uploaded to S3: {len(s3_urls)} files")
                    for s3_url in s3_urls:
                        print(f"    {s3_url}")
                
                if output_paths:
                    print(f"✓ Local files: {len(output_paths)} files")
                    for path in output_paths:
                        print(f"    {path}")
                
                # Print sample statistics
                if len(dataset) > 0:
                    sample_text = dataset[0]['text']
                    avg_length = sum(len(sample['text']) for sample in dataset) / len(dataset)
                    print(f"\nDataset Statistics:")
                    print(f"  Total samples: {len(dataset)}")
                    print(f"  Files created: {num_files}")
                    print(f"  Max lines per file: {max_lines_per_file}")
                    print(f"  Average text length: {avg_length:.0f} characters")
                    print(f"  Sample text preview: {sample_text[:200]}...")
                
                # Clean up temp directory if used and all files were uploaded
                if s3_path and cleanup_local and actual_output_dir != output_dir and len(s3_urls) == num_files:
                    import shutil
                    shutil.rmtree(actual_output_dir)
                    print(f"✓ Temp directory cleaned up")
                
                # Return S3 URLs if available, otherwise local paths
                return s3_urls if s3_urls else output_paths
                
            else:
                # Single file output
                filename = f"c4_{split}_{num_samples}.jsonl"
                output_path = Path(actual_output_dir) / filename
                print(f"Saving dataset to {output_path}...")
                
                # Save as JSONL format
                with open(output_path, 'w', encoding='utf-8') as f:
                    for sample in dataset:
                        f.write(json.dumps(sample) + '\n')
                
                print(f"✓ Successfully downloaded {len(dataset)} samples")
                print(f"✓ Saved to: {output_path}")
                
                # Upload to S3 immediately if requested
                s3_url = None
                if s3_path and s3_client:
                    s3_key = f"{s3_prefix}/{filename}" if s3_prefix else filename
                    s3_url = upload_to_s3(str(output_path), s3_bucket, s3_key, s3_client)
                    
                    # Clean up local file immediately after successful upload
                    if cleanup_local and s3_url:
                        print(f"Cleaning up local file: {output_path}")
                        output_path.unlink()
                        if s3_path and cleanup_local and actual_output_dir != output_dir:
                            # Remove temp directory
                            import shutil
                            shutil.rmtree(actual_output_dir)
                            print(f"✓ Temp directory cleaned up")
                
                # Print sample statistics
                if len(dataset) > 0:
                    sample_text = dataset[0]['text']
                    avg_length = sum(len(sample['text']) for sample in dataset) / len(dataset)
                    print(f"\nDataset Statistics:")
                    print(f"  Total samples: {len(dataset)}")
                    print(f"  Average text length: {avg_length:.0f} characters")
                    print(f"  Sample text preview: {sample_text[:200]}...")
                
                # Return S3 URL if available, otherwise local path
                return s3_url if s3_url else str(output_path)
        
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
    
    parser.add_argument(
        "--s3-path",
        type=str,
        help="S3 path in format 's3://bucket-name/path' to upload the dataset"
    )
    
    parser.add_argument(
        "--cleanup-local",
        action="store_true",
        help="Delete local file after successful S3 upload"
    )
    
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep local file even when uploading to S3 (overrides default cleanup behavior)"
    )
    
    parser.add_argument(
        "--max-lines-per-file",
        type=int,
        help="Maximum number of lines per JSONL file (splits into multiple files if exceeded)"
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
    
    # Determine cleanup mode - default to True when S3 path is specified, unless --no-cleanup is used
    if args.no_cleanup:
        cleanup_mode = False
    else:
        cleanup_mode = args.cleanup_local or bool(args.s3_path)
    
    # Setup HuggingFace authentication
    setup_hf_token()
    
    # Download the dataset
    result = download_c4_subset(
        output_dir=args.output_dir,
        num_samples=args.num_samples,
        split=args.split,
        streaming=streaming_mode,
        cache_dir=args.cache_dir,
        s3_path=args.s3_path,
        cleanup_local=cleanup_mode,
        max_lines_per_file=args.max_lines_per_file
    )
    
    print(f"\n✓ Dataset available at: {result}")


if __name__ == "__main__":
    main()