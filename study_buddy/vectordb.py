from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from constants import QDRANT_API_URL, QDRANT_API_KEY


class RAG:
    """
    Represents a RAG (Rapid Automatic Grader) object.
    Attributes:
        qdrant_client (QdrantClient): The QdrantClient object for Qdrant Cloud.
    Methods:
        pdf_loader(file_path): Loads a PDF file and returns the extracted documents.
        hf_embedding(): Returns the HuggingFaceEmbeddings object for the specified model.
        vector_store(collection_name, pdf_path): Store vectors in the Qdrant index.
        vector_retriever(query, collection_name, k=3): Perform a vector search using the QdrantClient.
    """

    def __init__(self):
        self.qdrant_client = QdrantClient(url=QDRANT_API_URL,
                                          api_key=QDRANT_API_KEY)

    def pdf_loader(self, file_path):
        """
        Loads a PDF file and returns the extracted documents.
        Args:
            file_path (str): The path to the PDF file.
        Returns:
            list: A list of extracted documents.
        """

        loader = PyPDFLoader(
            file_path=file_path,
            extract_images=True,
        )
        return loader.load_and_split()

    def hf_embedding(self):
        """
        Returns the HuggingFaceEmbeddings object for the specified model.

        Returns:
            HuggingFaceEmbeddings: The HuggingFaceEmbeddings object.
        """
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-xlm-r-multilingual-v1",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={"normalize_embeddings": False})

        return embeddings

    def vector_store(self, collection_name, pdf_path):
        """
        Store vectors in the Qdrant index.

        Returns:
            qdrant_rsp: Response from Qdrant indicating the success of the operation.
        """
        documents = self.pdf_loader(pdf_path)
        qdrant_rsp = Qdrant.from_documents(
            documents,
            self.hf_embedding(),
            url=QDRANT_API_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=True,
            collection_name=collection_name,
        )

        return qdrant_rsp

    def vector_retriever(self, query, collection_name):
        """
        Perform a vector search using the QdrantClient.

        Args:
            k (int): The number of results to return.

        Returns:
            doc_retriever: A Qdrant retriever object for similarity search.
        """
        doc_store = Qdrant(client=self.qdrant_client,
                           collection_name=collection_name,
                           embeddings=self.hf_embedding())

        # # similarity search works best for this case
        # doc_retriever = doc_store.as_retriever(
        #     search_type="similarity",
        #     search_kwargs={
        #         "k": k
        #     }
        # )

        # return doc_retriever

        found_docs = doc_store.similarity_search(query)
        return found_docs


if __name__ == "__main__":
    rag = RAG()
    embedding_collection_name = "pdfs"
    pdf_path = "/home/runner/StudyBuddy/courses/6044071222/11/AE_Lecture_02_Polish_exam.pdf"
    # rag.vector_store(embedding_collection_name, pdf_path)
    doc_retriever = rag.vector_retriever("Random-effects GLS regression",
                                         embedding_collection_name)
    print(doc_retriever[0].page_content)
