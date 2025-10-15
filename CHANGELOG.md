# Changelog

## [0.6.0] - 2025-10-15
- New gpt-4o model
- New `vl_high_resolution_images` parameter for qwen/qwen3-vl models
- New provider: Gemini and gemini-2.5 & gemini-2.0 models

## [0.5.0] - 2025-10-02

### Added
- Add OpenAI-compatible provider for custom OpenAI API endpoints

## [0.4.2] - 2025-10-2

### Added
- New Qwen3 models
- Connection tests for new models

### Fixed
- Streaming option in Qwen and Doubao provider

## [0.4.1] - 2025-09-25

### Removed
- Deprecate test_connection, keep only CLI test connection

## [0.4.0] - 2025-09-25

### Added
- Multi-image support for vision models - process multiple images in a single request
- Streaming output support for real-time response generation
- System prompt support - configure system prompts during session initialization
- Connection testing CLI commands (`-t/--test` and `-q/--quick-test`)
- Thinking mode flag (`-k/--thinking`) for models that support reasoning
- Comprehensive test connection methods for different providers and models

### Changed
- Improved CLI argument handling with proper long-form flags
- Extended session model with system prompt field

## [0.3.0] - 2025-09-12

### Fixed
- OpenAI GPT-5 temperature handling and reasoning token display
- Test infrastructure and token limits

## [0.2.0] - 2025-09-12

### Added
- Enhanced provider interface

## [0.1.0] - 2025-09-06

### Added
- Initial release with unified LLM provider interface
- Multi-agent system support
- CLI interface
