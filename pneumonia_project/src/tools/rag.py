import os
import glob
import json
import hashlib
import numpy as np
from PIL import Image
from datetime import datetime
from rank_bm25 import BM25Okapi
from src import config

from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

class RagTool:
    def __init__(self):
        self.kb_path = config.KB_PATH
        self.db_path = config.VECTOR_DB_PATH
        self.status_file = os.path.join(self.db_path, "db_status.json")

        # 1. Inizializzazione Embeddings (Caricamento modello in memoria)
        print("[RAG] Inizializzazione FastEmbed (Multilingual-E5)...")
        self.embeddings = FastEmbedEmbeddings(model_name="intfloat/multilingual-e5-large")

        # 2. Connessione a ChromaDB
        self.vector_db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings,
            collection_name="medical_knowledge"
        )

        # Inizializziamo il BM25 per la ricerca a parole chiave
        self.bm25 = None
        self.corpus_docs = []
        self._initialize_bm25()

        # 3. Controllo per Rebuild
        if self._should_rebuild():
            self._build_index()
            self._initialize_bm25()
        else:
            print(f"[RAG] Knowledge Base aggiornata. Caricate {len(self.vector_db.get()['ids'])} sezioni.")

    def _initialize_bm25(self):
        """Inizializza l'indice BM25 dai documenti presenti nel Vector DB."""
        data = self.vector_db.get()
        if not data or not data['documents']:
            return

        print(f"[RAG] Inizializzazione BM25 su {len(data['documents'])} sezioni...")
        self.corpus_docs = []
        tokenized_corpus = []

        for i, text in enumerate(data['documents']):
            metadata = data['metadatas'][i]
            # Creiamo un "documento virtuale" per BM25
            tokenized_text = text.lower().split()
            tokenized_corpus.append(tokenized_text)
            self.corpus_docs.append({
                "page_content": text,
                "metadata": metadata
            })

        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)

    def _get_kb_fingerprint(self):
        """Crea un'impronta digitale della cartella MD (nomi file + date modifica)."""
        md_files = glob.glob(os.path.join(self.kb_path, "*.md"))
        fingerprint = {}
        for f in md_files:
            # Usiamo la data di ultima modifica e la dimensione del file
            stats = os.stat(f)
            fingerprint[os.path.basename(f)] = f"{stats.st_mtime}-{stats.st_size}"
        return fingerprint

    def _should_rebuild(self):
        """Verifica se il database deve essere ricostruito."""
        # Se la cartella del DB non esiste o è vuota
        if not os.path.exists(self.db_path) or len(self.vector_db.get()['ids']) == 0:
            return True

        # Se manca il file di stato
        if not os.path.exists(self.status_file):
            return True

        try:
            with open(self.status_file, 'r') as f:
                old_fingerprint = json.load(f)

            new_fingerprint = self._get_kb_fingerprint()

            # Confronto: se i file sono diversi o le date di modifica sono cambiate
            return old_fingerprint != new_fingerprint
        except:
            return True

    def _build_index(self):
        print(f"[RAG] Rebuild in corso: Indicizzazione Knowledge Base...")

        # Svuotiamo il database esistente per evitare duplicati
        ids = self.vector_db.get()['ids']
        if ids:
            self.vector_db.delete(ids)

        all_splits = []
        md_files = glob.glob(os.path.join(self.kb_path, "*.md"))

        # Mapping dei file alle categorie per il filtraggio via metadati
        file_categories = {
            "tecnica_radiologica.md": "tecnica",
            "anatomia_ingannevole.md": "anatomia",
            "vocabolario_fleischner.md": "refertazione",
            "dispositivi_medici.md": "tecnica"
        }

        # Splitter pre-configurato per mantenere la gerarchia del documento
        headers_to_split_on = [
            ("#", "Category"),
            ("##", "Topic"),
            ("###", "Action")
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        for file_path in md_files:
            file_name = os.path.basename(file_path)
            category = file_categories.get(file_name, "generale")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    # Splittiamo il testo mantenendo i metadati degli header
                    splits = markdown_splitter.split_text(text)
                    for split in splits:
                        split.metadata["source"] = file_name
                        split.metadata["category"] = category
                        # Parent Document Retrieval: salviamo l'intero testo della sezione come metadato
                        split.metadata["full_section"] = split.page_content
                    all_splits.extend(splits)
            except Exception as e:
                print(f"[RAG] Errore lettura {file_name}: {e}")

        if all_splits:
            self.vector_db.add_documents(all_splits)

            # Salviamo il nuovo stato
            fingerprint = self._get_kb_fingerprint()
            with open(self.status_file, 'w') as f:
                json.dump(fingerprint, f)

            print(f"[RAG] Indice ricostruito con successo ({len(all_splits)} sezioni).")

    def _rerank_documents(self, query_embedding, docs):
        """Ri-ordina i documenti basandosi sulla similitudine cosina."""
        if not docs: return []

        scored_docs = []
        for doc in docs:
            # Se doc è un dizionario (da BM25) o un oggetto Document (da Chroma)
            if hasattr(doc, 'page_content'):
                content = doc.page_content
            else:
                content = doc.get('page_content', '')

            doc_embedding = self.embeddings.embed_query(content)
            score = sum(a*b for a, b in zip(query_embedding, doc_embedding))
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [d for s, d in scored_docs]

    def search(self, query: str | list, k: int = 4, category: str = None):
        """
        Cerca informazioni rilevanti con Ricerca Ibrida:
        - Keyword Search (BM25) per precisione terminologica
        - Vector Search (MMR) per affinità semantica
        - Semantic Re-ranking per ordinamento finale
        """
        filter_dict = {}
        if category:
            filter_dict["category"] = category
            print(f"[RAG] Filtro attivo per categoria: {category}")

        queries = [query] if isinstance(query, str) else query
        print(f"[RAG] Ricerca avanzata Multi-Query per: {queries}")
        all_docs = []

        # 1. Ricerca Vettoriale (MMR)
        for q in queries:
            v_docs = self.vector_db.max_marginal_relevance_search(
                q, k=k, fetch_k=10, filter=filter_dict if filter_dict else None
            )
            all_docs.extend(v_docs)

        # 2. Ricerca per Parole Chiave (BM25) - Fallback/Integrazione
        if self.bm25:
            for q in queries:
                tokenized_query = q.lower().split()
                # Prendiamo i top k risultati da BM25
                bm25_scores = self.bm25.get_scores(tokenized_query)
                top_n_ids = np.argsort(bm25_scores)[-k:][::-1]

                for idx in top_n_ids:
                    if bm25_scores[idx] > 0:
                        doc_data = self.corpus_docs[idx]
                        # Filtro per categoria se applicabile
                        if category and doc_data['metadata'].get('category') != category:
                            continue
                        all_docs.append(doc_data)

        # Rimozione duplicati
        seen_content = set()
        unique_docs = []
        for doc in all_docs:
            if hasattr(doc, 'page_content'):
                content = doc.page_content
            else:
                content = doc.get('page_content', '')

            if content not in seen_content:
                unique_docs.append(doc)
                if content:
                    seen_content.add(content)

        # 3. Re-ranking Semantico Finale
        top_query_emb = self.embeddings.embed_query(queries[0])
        reranked_docs = self._rerank_documents(top_query_emb, unique_docs)

        context_text = ""
        for doc in reranked_docs[:k]:
            if hasattr(doc, 'metadata'):
                metadata = doc.metadata
                content = doc.page_content
            else:
                metadata = doc.get('metadata', {})
                content = doc.get('page_content', '')

            source = metadata.get("source", "Protocollo")
            full_content = metadata.get("full_section", content)
            context_text += f"\n--- PROTOCOLLO [{source}] ---\n{full_content}\n"

        return context_text if context_text else "Nessuna linea guida specifica trovata."

    def get_visual_reference(self, analysis_text: str):
        """Mappa il testo dell'analisi a un'immagine di riferimento dell'atlante."""
        mapping = {
            "consolidamento": "consolidamento.png",
            "alveolare": "consolidamento.png",
            "versamento": "versamento.png",
            "costofrenic": "versamento.png",
            "interstizial": "interstiziale.png",
            "reticolare": "interstiziale.png",
            "dispositivo": "dispositivo.png",
            "pacemaker": "dispositivo.png",
            "cavi": "dispositivo.png",
            "elettrodi": "dispositivo.png"
        }

        atlas_path = os.path.join(os.path.dirname(self.kb_path), "visual_atlas")
        analysis_lower = analysis_text.lower()

        for key, filename in mapping.items():
            if key in analysis_lower:
                full_path = os.path.join(atlas_path, filename)
                if os.path.exists(full_path):
                    return Image.open(full_path)
        return None