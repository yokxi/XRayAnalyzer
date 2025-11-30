import os
import re 
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class RagTool:
    def __init__(self, kb_folder="knowledge_base"):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.kb_dir = os.path.join(self.base_path, kb_folder)
        
        print("🧠 RAG: Caricamento modello di embedding...")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.vector_db = self._build_index()

    def _build_index(self):
        """Legge i file, li spezza e crea l'indice FAISS"""
        if not os.path.exists(self.kb_dir):
            print(f"⚠️ Cartella {self.kb_dir} non trovata.")
            return None

        documents = []
        print(f"📂 RAG: Scansione documenti in {self.kb_dir}...")

        for filename in os.listdir(self.kb_dir):
            file_path = os.path.join(self.kb_dir, filename)
            try:
                if filename.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                    print(f"   📄 Caricato PDF: {filename}")
                elif filename.lower().endswith(".txt"):
                    loader = TextLoader(file_path, encoding="utf-8")
                    documents.extend(loader.load())
                    print(f"   📄 Caricato TXT: {filename}")
            except Exception as e:
                print(f"❌ Errore caricamento {filename}: {e}")

        if not documents:
            print("⚠️ Nessun documento trovato.")
            return None

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        print(f"✂️  Creati {len(chunks)} frammenti di testo.")

        print("🚀 RAG: Creazione indice vettoriale FAISS...")
        vector_db = FAISS.from_documents(chunks, self.embeddings)
        print("✅ Database Vettoriale Pronto!")
        
        return vector_db

    def search(self, query, k=2):
        """Cerca i pezzi di testo più simili alla query e li pulisce"""
        if not self.vector_db:
            return "Database non disponibile."

        results = self.vector_db.similarity_search(query, k=k)
        
        cleaned_texts = []
        for doc in results:
            content = doc.page_content
            
            clean_content = re.sub(r'\[.*?\]', '', content)
            
            clean_content = clean_content.strip()
            
            cleaned_texts.append(clean_content)
    
        return "\n\n".join(cleaned_texts)