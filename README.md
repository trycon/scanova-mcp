# Scanova MCP Server

A Model Context Protocol (MCP) server for creating and managing QR codes using the Scanova API. This server provides tools for QR code creation, management, and download through MCP-compatible IDEs like Cursor and VS Code.

## Features

- ✅ **Create QR Codes**: Generate dynamic QR codes with custom URLs
- ✅ **List QR Codes**: View all your existing QR codes with pagination
- ✅ **Update QR Codes**: Modify existing QR codes with new URLs or names
- ✅ **Retrieve QR Code Details**: Get detailed information about specific QR codes
- ✅ **Download QR Codes**: Download QR code images in various formats
- ✅ **Activate/Deactivate QR Codes**: Control QR code status

## Prerequisites

- Scanova API key (get one from [https://app.scanova.io/](https://app.scanova.io/))
- MCP-compatible IDE (Cursor, VS Code, Claude Desktop, etc.)

## Quick Setup

### Step 1: Get Your Scanova API Key
1. Visit [https://app.scanova.io/](https://app.scanova.io/)
2. Sign up or log in to your account
3. Navigate to API settings [https://app.scanova.io/settings/api] and generate your API key.

### Step 2: Configure Your IDE

Add the following configuration to your IDE's MCP settings:

**For Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "scanova-mcp": {
      "transport": "http",
      "url": "https://mcp.scanova.io/mcp",
      "headers": {
        "Authorization": "YOUR_SCANOVA_API_KEY_HERE"
      }
    }
  }
}
```

**For VS Code** (`~/.vscode/mcp.json`):
```json
{
  "mcpServers": {
    "scanova-mcp": {
      "transport": "http", 
      "url": "https://mcp.scanova.io/mcp",
      "headers": {
        "Authorization": "YOUR_SCANOVA_API_KEY_HERE"
      }
    }
  }
}
```

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "scanova-mcp": {
      "transport": "http",
      "url": "https://mcp.scanova.io/mcp", 
      "headers": {
        "Authorization": "YOUR_SCANOVA_API_KEY_HERE"
      }
    }
  }
}
```

## Tools


| Tool                 | Description                | Example Phrases                                         |
|----------------------|---------------------------|---------------------------------------------------------|
| `create_qr_code`     | Create a new QR code      | "create qr", "make qr code", "generate qr"              |
| `list_qr_codes`      | List existing QR codes    | "list qr codes", "show qr codes", "recent qr codes"     |
| `update_qr_code`     | Update existing QR code   | "update qr", "modify qr code", "edit qr code"           |
| `retrieve_qr_code`   | Get QR code details       | "get qr details", "qr code info"                        |
| `download_qr_code`   | Download QR code image    | "download qr", "get qr image"                           |
| `activate_qr_code`   | Activate a QR code        | "activate qr", "enable qr code"                         |
| `deactivate_qr_code` | Deactivate a QR code      | "deactivate qr", "disable qr code"                      |


## Usage

The server provides the following MCP tools that you can use in your MCP-compatible IDE:


## API Endpoints

The deployed server provides these endpoints:

- **POST `/mcp`** - Main MCP JSON-RPC endpoint
- **GET `/health`** - Health check endpoint
- **GET `/`** - Service information and documentation

## Local Development (Optional)

If you want to run the server locally for development:

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd qcg-mcp
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run locally**:
   ```bash
   # HTTP server mode
   uv run cloud_server.py
   
   # Or stdio mode for local MCP testing
   uv run main.py
   ```

4. **Configure for local testing**:
   ```json
   {
     "mcpServers": {
       "qcg-mcp": {
         "transport": "http",
         "url": "http://localhost:8000/mcp",
         "headers": {
           "Authorization": "YOUR_SCANOVA_API_KEY_HERE"
         }
       }
     }
   }
   ```

### Docker Deployment (Local)

1. **Build the Docker image**:
   ```bash
   docker build -t mcpserver:local .
   ```

2. **Start the container**:
   ```bash
   docker run -d --name mcpserver -p 8000:8000 mcpserver:local
   ```

   Or with Docker Compose:
   ```bash
   docker compose up -d
   ```

3. **Verify the server is running**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Configure your IDE (HTTP transport)**:
   Use the "Configure for local testing" snippet above and point to `http://localhost:8000/mcp`, ensuring the `Authorization` header contains your Scanova API key.

5. **View logs and stop**:
   ```bash
   # View logs
   docker logs -f mcpserver

   # Stop and remove with Compose
   docker compose down

   # Or stop/remove single container
   docker stop mcpserver && docker rm mcpserver
   ```

## Troubleshooting

### Common Issues

1. **"API key is required"**
   - Ensure your Scanova API key is correctly set in the headers
   - Check that the header format matches one of the supported formats
   - Get your API key from [https://app.scanova.io/](https://app.scanova.io/)

2. **"Invalid token" error**
   - Verify your API key is valid and active
   - Ensure there are no extra spaces or characters in the API key
   - Try regenerating your API key from the Scanova dashboard

3. **Connection errors**
   - Check that the server URL is correct
   - Ensure your internet connection is working
   - Verify the server is deployed and running

4. **Tool not found**
   - Restart your IDE after adding the MCP configuration
   - Check that the JSON configuration is valid
   - Verify the server responds at the `/health` endpoint

## License

This project is licensed under the terms of the MIT open source license. Please refer to [MIT](./LICENSE) for the full terms.
