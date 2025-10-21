# Place your documents here

This directory is for documents you want to index into the RAG system.

## Supported Formats

- PDF (`.pdf`)
- Text files (`.txt`)
- Word documents (`.docx`)

## How to Use

1. Copy your documents to this folder:
   ```bash
   cp /path/to/your/file.pdf ./data/docs/
   ```

2. Run the document loader:
   ```bash
   docker exec -it openwebui-backend-1 python loader.py
   ```

3. The documents will be processed, chunked, and indexed into Qdrant

## Example

```bash
# Add a PDF
cp ~/Downloads/user-manual.pdf ./data/docs/

# Add multiple files
cp ~/Documents/*.pdf ./data/docs/

# Index them
docker exec -it openwebui-backend-1 python loader.py
```

## Notes

- Large documents will be automatically chunked into smaller pieces
- The loader recursively processes all subdirectories
- You can organize files in subfolders if needed
- Re-running the loader will add new documents to the existing index
