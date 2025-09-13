import os
import glob
import json
import argparse
import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# --- 1. DATA LOADING AND NORMALIZATION ---

def load_processed_data(input_folders: list[str]) -> list[dict]:
    """
    Loads all JSON files from multiple preprocessed directories and normalizes them.
    """
    all_docs = []
    for folder in input_folders:
        print(f"Loading data from: {folder}...")
        json_files = glob.glob(os.path.join(folder, "*.json"))
        for file_path in json_files:
            try: # <-- START OF THE NEW, ROBUST CODE
                with open(file_path, 'r', encoding='utf-8') as f:
                    # First check if the file is empty
                    if os.path.getsize(file_path) == 0:
                        print(f"WARNING: Skipping empty file: {os.path.basename(file_path)}")
                        continue # Move to the next file
                    
                    data = json.load(f)
            
            except json.JSONDecodeError:
                print(f"WARNING: Skipping corrupt JSON file: {os.path.basename(file_path)}")
                continue # Move to the next file
            except Exception as e:
                print(f"WARNING: An unexpected error occurred with file {os.path.basename(file_path)}: {e}")
                continue
            # <-- END OF THE NEW, ROBUST CODE
                
            source = data.get("source_file", os.path.basename(file_path))
            content = ""
            doc_type = "unknown"

            if "cleaned_text" in data:
                content = data["cleaned_text"]
                doc_type = "text_document"
            elif "records" in data:
                content = json.dumps(data["records"])
                doc_type = "spreadsheet"
            elif "original_data" in data:
                content = json.dumps(data["original_data"])
                doc_type = "json_object"
            
            if content:
                all_docs.append({"source": source, "content": content, "type": doc_type})
    
    print(f"Loaded a total of {len(all_docs)} documents.")
    return all_docs

# ... (The rest of the file remains exactly the same) ...
# --- 2. TEXT CHUNKING ---
# --- 3. EMBEDDING AND INDEXING ---
# --- 4. VALIDATION ---
# --- COMMAND-LINE INTERFACE ---

def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Splits the 'content' of text documents into smaller chunks for better retrieval.
    Structured data (like excel/json) is not chunked.
    """
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    
    chunked_docs = []
    for doc in documents:
        if doc["type"] == "text_document":
            chunks = text_splitter.split_text(doc["content"])
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "source": f"{doc['source']} (chunk {i+1})",
                    "content_chunk": chunk
                })
        else:
            # For structured data, the whole content is one "chunk"
            chunked_docs.append({
                "source": doc["source"],
                "content_chunk": doc["content"]
            })
            
    print(f"Total chunks created: {len(chunked_docs)}")
    return chunked_docs

def build_and_save_kb(chunks: list[dict], output_folder: str):
    """
    Generates embeddings for all chunks and saves them to a FAISS index,
    along with the corresponding text chunks.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    print("Loading embedding model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    content_to_embed = [chunk['content_chunk'] for chunk in chunks]
    print(f"Generating embeddings for {len(content_to_embed)} chunks...")
    embeddings = model.encode(content_to_embed, show_progress_bar=True)
    
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    faiss_index_path = os.path.join(output_folder, "kb.faiss")
    chunks_path = os.path.join(output_folder, "kb_chunks.json")
    
    faiss.write_index(index, faiss_index_path)
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2)
        
    print(f"Knowledge Base built successfully!")
    print(f"FAISS index saved to: {faiss_index_path}")
    print(f"Text chunks saved to: {chunks_path}")

def validate_kb(kb_folder: str, query: str):
    """
    Loads the created KB and performs a test search to validate it.
    """
    print("\n--- Running Validation ---")
    try:
        index = faiss.read_index(os.path.join(kb_folder, "kb.faiss"))
        with open(os.path.join(kb_folder, "kb_chunks.json"), 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"Performing test search for query: '{query}'")
        query_embedding = model.encode([query])
        
        distances, indices = index.search(np.array(query_embedding), k=3)
        
        print("Top 3 results found:")
        for i in indices[0]:
            if i != -1:
                print(f"  - Source: {chunks[i]['source']}")
                print(f"    Content: '{chunks[i]['content_chunk'][:150]}...'")

    except Exception as e:
        print(f"Validation failed. Reason: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a local Knowledge Base from preprocessed data.")
    parser.add_argument("input_folders", nargs='+', type=str, help="One or more paths to folders containing preprocessed .json files.")
    parser.add_argument("output_folder", type=str, help="The path to the folder where the final KB (FAISS index and chunks) will be saved.")
    
    args = parser.parse_args()
    
    normalized_documents = load_processed_data(args.input_folders)
    if normalized_documents:
        chunked_documents = chunk_documents(normalized_documents)
        build_and_save_kb(chunked_documents, args.output_folder)
        validate_kb(args.output_folder, query="glucose")

        