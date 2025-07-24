# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OpenRouter API proxy monitoring system that provides reverse proxy functionality with real-time monitoring and a web interface. The system intercepts OpenAI/OpenRouter API requests, logs them, and provides a monitoring dashboard.

## Architecture

The system uses a dual-server architecture:
- **Proxy Server** (port 8080): Handles API requests and forwards them to OpenRouter
- **Web Server** (port 8081): Provides monitoring interface and API endpoints

### Core Components

- `run.py`: Main entry point that starts both servers concurrently
- `proxy_server.py`: OpenAI API reverse proxy with request/response logging
- `web_server.py`: Web interface server with authentication middleware
- `models.py`: Data models and SQLite storage for request records
- `config.py`: Configuration management with environment variable support

### Key Features

- Request/response logging with SQLite persistence
- API key-based authentication and filtering
- Real-time monitoring dashboard
- Request search and pagination
- Statistics and analytics

## Development Commands

### Start the Application
```bash
python run.py
```

### Run Tests
```bash
python test_proxy.py      # Test proxy functionality
python test_streaming.py  # Test streaming responses
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

All configuration is centralized in `config.py`:
- Server ports and hosts (configurable via environment variables)
- OpenRouter API base URL (currently: https://openrouter.ai/api/v1)
- Default API keys and admin authentication
- Database and pagination settings

## Database Schema

The system uses SQLite with a `RequestRecord` model that stores:
- Request metadata (method, URL, headers, body)
- Response data (status, headers, body, duration)
- API key association for filtering
- Timestamps and error logging

## Authentication System

- Cookie-based authentication using API keys
- Super admin key can view all requests
- Individual API keys can only view their own requests
- Login page at `/login` with middleware protection

## API Endpoints

Web server provides REST endpoints:
- `GET /api/requests` - Paginated request list with filtering
- `GET /api/request/{id}` - Individual request details
- `GET /api/stats` - Usage statistics and metrics