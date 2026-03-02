"""
Pure Python vector retrieval - NO Chroma, NO database, NO HNSW errors!
100% stable, ultra fast for <100k documents
"""
import os
import json
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

# Force offline mode
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

class ONNXEmbedding:
    def __init__(self):
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load tokenizer from local path
        tokenizer_path = os.path.join(script_dir, "bge-large-zh-v1.5")
        print(f"加载嵌入模型: {os.path.join(script_dir, 'bge-large-zh-v1.5-onnx')}")
        print("使用ONNX Runtime轻量推理引擎")
        
        original_cwd = os.getcwd()
        os.chdir(tokenizer_path)
        self.tokenizer = AutoTokenizer.from_pretrained(
            "./", 
            trust_remote_code=True,
            local_files_only=True
        )
        os.chdir(original_cwd)
        
        # Load ONNX model
        onnx_model_path = os.path.join(script_dir, "bge-large-zh-v1.5-onnx", "model.onnx")
        self.session = ort.InferenceSession(
            onnx_model_path,
            providers=["CPUExecutionProvider"]
        )
        
        self.input_names = [input.name for input in self.session.get_inputs()]
        self.output_name = self.session.get_outputs()[0].name
        print("嵌入模型加载完成")
    
    def encode(self, texts):
        """Encode texts to 1024d vectors"""
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="np"
        )
        
        # Convert all inputs to int64 for ONNX compatibility
        onnx_inputs = {}
        for name in self.input_names:
            onnx_inputs[name] = inputs[name].astype(np.int64)
        
        # Run inference
        outputs = self.session.run([self.output_name], onnx_inputs)
        
        # Get <[BOS_never_used_51bce0c785ca2f68081bfa7d91973934]> token embedding
        embeddings = outputs[0][:, 0]
        
        # Normalize
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norm
        
        return embeddings

class PureVectorStore:
    def __init__(self):
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load embedding model
        self.embedding_model = ONNXEmbedding()
        
        # Load pre-exported data
        print("Loading RAG database files...")
        docs_path = os.path.join(script_dir, "rag_database_docs.json")
        with open(docs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.documents = data["documents"]
            self.metadatas = data["metadatas"]
        
        # Load embeddings as numpy array
        embeddings_path = os.path.join(script_dir, "rag_database_embeddings.npy")
        self.embeddings = np.load(embeddings_path)
        print(f"Loaded {len(self.documents)} documents, dimension: {self.embeddings.shape[1]}")
        
        # Normalize embeddings for cosine similarity
        norm = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings_normalized = self.embeddings / norm
        print("Database loaded and ready!")
    
    def query(self, query_text, n_results=5, min_similarity=0.5):
        """Query similar documents using pure numpy cosine similarity"""
        # Generate query embedding
        query_embedding = np.array(self.embedding_model.encode([query_text])[0], dtype=np.float32)
        
        # Normalize query embedding
        query_norm = np.linalg.norm(query_embedding)
        query_embedding_normalized = query_embedding / query_norm
        
        # Calculate cosine similarity (dot product of normalized vectors)
        similarities = np.dot(self.embeddings_normalized, query_embedding_normalized)
        
        # Get top N results with similarity threshold
        top_indices = np.argsort(similarities)[-n_results:][::-1]
        
        # Return format exactly matches original Chroma interface: list of dicts with 'text' and 'metadata'
        results = []
        for i in top_indices:
            if similarities[i] >= min_similarity:
                results.append({
                    "text": self.documents[i],
                    "metadata": self.metadatas[i],
                    "similarity": float(similarities[i])
                })
        
        return results
    
    def search(self, query_text, n_results=5, **kwargs):
        """Alias for query method, compatible with old Chroma interface, ignore extra params"""
        return self.query(query_text, n_results)

# Global instance
vs = None

def get_vector_store():
    global vs
    if vs is None:
        vs = PureVectorStore()
    return vs