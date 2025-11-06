# Development Standards and Best Practices

## Code Organization

### Directory Structure
- `FSDP/src/`: Core training implementation
- `FSDP/kubernetes/`: Kubernetes deployment configurations
- `tools/`: Utility scripts and configurations
  - `tools/test_hyperpod_cluster.py`: Comprehensive HyperPod testing framework
  - `tools/validate_test_setup.py`: Testing framework validation
  - `tools/dataset/`: Dataset download and processing utilities
  - `tools/internal/`: Internal environment configuration scripts
  - `tools/k8s-shell/`: Kubernetes shell utilities
- `doc/`: Comprehensive documentation
  - `doc/README.md`: Documentation index
  - `doc/TESTING_GUIDE.md`: Testing procedures and workflows
  - `doc/TESTING_SUMMARY.md`: Framework overview and components
- `tmp/`: Temporary and historical documentation
  - `tmp/VERIFICATION_RESULTS.md`: Verified test results (archived)
  - `tmp/CLEANUP_SUMMARY.md`: Development process documentation
- `Makefile`: Standardized commands for testing and deployment

### Module Structure
- `model_utils/`: Reusable utility functions
  - `arguments.py`: Command-line argument parsing
  - `checkpoint.py`: Checkpointing functionality (both standard and MTC)
  - `train_utils.py`: Training utilities and helpers
  - `concat_dataset.py`: Dataset concatenation utilities

## Documentation Standards

### Documentation Organization
- All project documentation should be placed in the `doc/` directory
- Use clear, descriptive filenames with `.md` extension
- Include a `doc/README.md` as the documentation index
- Create guides for major features and configuration changes
- Update the documentation index when adding new guides

### Documentation Types
- **User Guides**: Step-by-step instructions for common tasks
- **Configuration Guides**: Parameter explanations and examples
- **Testing Guides**: Framework usage and validation procedures
- **Integration Guides**: Platform-specific deployment instructions
- **Reference Guides**: Command and API references

### Documentation Standards
- Use clear, concise language appropriate for developers
- Include practical examples and code snippets
- Provide both template and concrete usage examples
- Document migration paths for breaking changes
- Include troubleshooting sections for complex features

## Coding Standards

### Python Code Style
- Follow PEP 8 conventions
- Use type hints where appropriate
- Include docstrings for all functions and classes
- Use meaningful variable and function names
- Keep functions focused and single-purpose

### Error Handling
- Use proper exception handling with specific exception types
- Log errors with appropriate log levels
- Implement graceful degradation where possible
- Include context in error messages

### Logging
- Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include rank information in distributed training logs
- Log performance metrics (throughput, loss, learning rate)
- Use consistent log formatting across modules

## Configuration Management

### Model Configurations
- Store model parameters in separate configuration files
- Use consistent parameter naming across models
- Include model size and architecture details in configurations
- Support both predefined and custom model configurations

### Training Parameters
- Use command-line arguments for runtime configuration
- Provide sensible defaults for all parameters
- Group related parameters logically
- Include parameter validation and bounds checking

### Dataset Management
- Use the `tools/dataset/` utilities for dataset preparation
- Support streaming datasets from HuggingFace Hub
- Implement proper dataset caching strategies
- Include dataset validation and preprocessing steps

## Distributed Training Standards

### FSDP Configuration
- Use appropriate sharding strategies (full vs hybrid)
- Configure mixed precision consistently
- Implement proper gradient clipping
- Use activation checkpointing for memory optimization

### Checkpointing
- Support both standard and Managed Tiered Checkpointing (MTC)
- Implement automatic checkpoint resume
- Use consistent checkpoint directory structure
- Include metadata in checkpoints for debugging

### Performance Optimization
- Configure EFA networking for multi-node training
- Use appropriate batch sizes for hardware
- Implement gradient accumulation when needed
- Monitor and log performance metrics

## Testing Standards

### HyperPod Testing Framework
- Use `make validate-framework` to validate testing setup
- Use `make test-quick` for rapid validation (1 minute)
- Use `make test-cluster` for comprehensive testing (5 minutes)
- Use `make perf-test` for performance validation
- All testing should be done on actual HyperPod clusters for realistic validation

### Testing Workflow
```bash
# 1. Framework validation
make validate-framework

# 2. Cluster health check
make validate-setup

# 3. Quick end-to-end test
make test-quick

# 4. Deploy and monitor
make run
make logs-follow
make stop
```

### Unit Testing
- Test utility functions in isolation using pytest
- Mock external dependencies (datasets, model loading)
- Test error conditions and edge cases
- Use the testing framework in `tools/` for validation

### Integration Testing
- Use the HyperPod testing framework for end-to-end validation
- Test complete training workflows on actual clusters
- Validate checkpoint save/load functionality with real storage
- Test distributed training setup with actual multi-node deployment
- Verify model parameter consistency across distributed setup

### Performance Testing
- Use `make perf-test` for standardized performance validation
- Benchmark training throughput on target hardware
- Test memory usage patterns with actual workloads
- Validate scaling across multiple nodes with real networking
- Monitor convergence behavior with production-like datasets

### Continuous Testing
- Integrate testing framework into CI/CD pipelines
- Use `make validate-framework` in automated checks
- Run `make test-quick` for pull request validation
- Schedule `make test-cluster` for comprehensive validation
- Monitor cluster health with `make validate-setup`