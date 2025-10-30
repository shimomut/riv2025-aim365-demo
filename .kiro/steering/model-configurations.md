# Model Configuration Guidelines

## Supported Model Architectures

### Llama Family Models

#### Llama 2 Models
**Llama 2 7B:**
```python
--hidden_width=4096
--num_layers=32
--num_heads=32
--intermediate_size=11008
--num_key_value_heads=32
--max_context_width=4096
--model_type=llama_v2
--tokenizer=meta-llama/Llama-2-7b-hf
```

**Llama 2 13B:**
```python
--hidden_width=5120
--num_layers=40
--num_heads=40
--intermediate_size=13824
--num_key_value_heads=40
--max_context_width=4096
--model_type=llama_v2
--tokenizer=meta-llama/Llama-2-13b-hf
```

**Llama 2 70B:**
```python
--hidden_width=8192
--num_layers=80
--num_heads=64
--intermediate_size=28672
--num_key_value_heads=8
--max_context_width=4096
--model_type=llama_v2
--tokenizer=meta-llama/Llama-2-70b-hf
```

#### Llama 3.1 Models
**Llama 3.1 8B:**
```python
--hidden_width=4096
--num_layers=32
--num_heads=32
--intermediate_size=14336
--num_key_value_heads=8
--max_context_width=8192
--model_type=llama_v3
--tokenizer=hf-internal-testing/llama-tokenizer
```

**Llama 3.1 70B:**
```python
--hidden_width=8192
--num_layers=80
--num_heads=64
--intermediate_size=28672
--num_key_value_heads=8
--max_context_width=8192
--model_type=llama_v3
--tokenizer=hf-internal-testing/llama-tokenizer
```

#### Llama 3.2 Models
**Llama 3.2 1B:**
```python
--hidden_width=2048
--num_layers=16
--num_heads=32
--intermediate_size=8192
--num_key_value_heads=8
--max_context_width=8192
--model_type=llama_v3
--tokenizer=hf-internal-testing/llama-tokenizer
```

**Llama 3.2 3B:**
```python
--hidden_width=3072
--num_layers=28
--num_heads=24
--intermediate_size=11008
--num_key_value_heads=8
--max_context_width=8192
--model_type=llama_v3
--tokenizer=hf-internal-testing/llama-tokenizer
```

### Mistral Family Models

#### Mistral 8x7B (Mixtral)
```python
--hidden_width=4096
--num_layers=32
--num_heads=32
--intermediate_size=14336
--num_key_value_heads=8
--max_context_width=32768
--vocab_size=32000
--model_type=mixtral
--tokenizer=mistralai/Mixtral-8x7B-v0.1
```

#### Mistral Mathstral 7B
```python
--hidden_width=4096
--num_layers=32
--num_heads=32
--intermediate_size=14336
--num_key_value_heads=8
--max_context_width=32768
--vocab_size=32768
--model_type=mistral
--tokenizer=mistralai/mathstral-7B-v0.1
```

## Model Configuration Best Practices

### Parameter Selection
- **Context Length**: Use model-appropriate context lengths (4K for Llama 2, 8K for Llama 3.x, 32K for Mistral)
- **Vocabulary Size**: Match the tokenizer vocabulary size exactly
- **GQA Configuration**: Use appropriate `num_key_value_heads` for Grouped Query Attention
- **Intermediate Size**: Follow the model architecture specifications

### Memory Optimization
```python
# Enable mixed precision training
--bf16=1

# Use activation checkpointing for large models
--activation_checkpointing=1

# Offload activations for memory-constrained environments
--offload_activations=1

# Configure FSDP sharding strategy
--sharding_strategy=full  # or hybrid for very large models
```

### Training Configuration
```python
# Optimizer settings
--lr=0.0001
--weight_decay=0.2
--beta1=0.9
--beta2=0.95
--grad_clip=1.0

# Learning rate schedule
--lr_decay_style=cosine
--min_lr=1e-5
--warmup=0.0032

# Batch size (adjust based on hardware)
--train_batch_size=1  # Per GPU batch size
--val_batch_size=1
```

## Hardware-Specific Configurations

### P5 Instances (8x H100)
```python
# Optimal settings for P5.48xlarge
--train_batch_size=2
--sharding_strategy=full
--activation_checkpointing=1
--offload_activations=0  # H100 has sufficient memory
```

### P4d Instances (8x A100)
```python
# Optimal settings for P4d.24xlarge
--train_batch_size=1
--sharding_strategy=full
--activation_checkpointing=1
--offload_activations=1  # May need activation offloading
```

### G5 Instances
```python
# Settings for G5.xlarge (1x A10G)
--train_batch_size=1
--sharding_strategy=full
--activation_checkpointing=1
--offload_activations=1
--cpu_offload=1  # May need CPU offloading for large models
```

## Dataset Configuration

### Streaming Datasets
```python
# Use streaming for large datasets
--dataset=allenai/c4
--dataset_config_name=en

# Alternative datasets
--dataset=openwebtext
--dataset=pile
```

### Custom Datasets
```python
# For custom HuggingFace datasets
--dataset=your-org/your-dataset
--dataset_config_name=your-config
```

## Checkpoint Configuration

### Standard Checkpointing
```python
--checkpoint_dir=./checkpoints
--checkpoint_freq=50
--resume_from_checkpoint=./checkpoints
```

### Managed Tiered Checkpointing (MTC)
```python
# MTC is enabled by default in the training script
# Configure frequencies in train.py:
in_memory_checkpointing_freq = 10  # Fast local checkpoints
s3_checkpointing_freq = 20         # Durable S3 checkpoints
```

## Validation and Monitoring

### Validation Configuration
```python
--validation_freq=25      # Validate every 25 steps
--validation_batches=10   # Use 10 batches for validation
```

### Logging Configuration
```python
--logging_freq=1          # Log every step
--max_steps=5000         # Total training steps
```

## Model-Specific Notes

### Llama Models
- Llama 3.x models use RoPE (Rotary Position Embedding) with base 10000
- Llama 2 models have different attention patterns than Llama 3.x
- Use appropriate tokenizers for each model family

### Mistral Models
- Mixtral uses sparse MoE (Mixture of Experts) architecture
- Requires gated model access through HuggingFace
- Higher memory requirements due to expert routing

### Performance Considerations
- Larger models benefit from hybrid sharding strategy
- Use gradient accumulation for effective larger batch sizes
- Monitor memory usage and adjust batch sizes accordingly
- Consider using CPU offloading for memory-constrained environments