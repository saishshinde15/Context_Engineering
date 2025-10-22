from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import os

# Lazy imports for performance
_vectorstore = None
_pruning_llm = None

def _get_vectorstore():
    """Lazy initialization of vector store to avoid loading on import."""
    global _vectorstore
    if _vectorstore is None:
        from langchain_community.document_loaders import WebBaseLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.vectorstores import InMemoryVectorStore
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        # Load Lilian Weng's blog posts
        urls = [
            "https://lilianweng.github.io/posts/2025-05-01-thinking/",
            "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
            "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
            "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
        ]
        
        docs = [WebBaseLoader(url).load() for url in urls]
        docs_list = [item for sublist in docs for item in sublist]
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=3000, 
            chunk_overlap=50
        )
        doc_splits = text_splitter.split_documents(docs_list)
        
        # Create vector store with Google Gemini embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        _vectorstore = InMemoryVectorStore.from_documents(
            documents=doc_splits, 
            embedding=embeddings
        )
    
    return _vectorstore

def _get_pruning_llm():
    """Lazy initialization of pruning LLM using Google Gemini."""
    global _pruning_llm
    if _pruning_llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        _pruning_llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    return _pruning_llm


class RAGRetrievalInput(BaseModel):
    """Input schema for RAG Retrieval Tool."""
    query: str = Field(..., description="The search query to retrieve relevant blog post content.")


class RAGRetrievalTool(BaseTool):
    name: str = "rag_retrieval_tool"
    description: str = (
        "Retrieves relevant content from Lilian Weng's blog posts about AI topics. "
        "Use this tool to search for information about reward hacking, hallucination, "
        "diffusion models, thinking mechanisms, and other AI research topics."
    )
    args_schema: Type[BaseModel] = RAGRetrievalInput

    def _run(self, query: str) -> str:
        """Retrieve relevant documents from the vector store."""
        try:
            vectorstore = _get_vectorstore()
            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(query)
            
            # Concatenate retrieved documents
            combined_content = "\n\n---\n\n".join([
                f"Document {i+1}:\n{doc.page_content}" 
                for i, doc in enumerate(docs)
            ])
            
            return combined_content
        except Exception as e:
            return f"Error retrieving documents: {str(e)}"


class ContextPruningInput(BaseModel):
    """Input schema for Context Pruning Tool."""
    user_request: str = Field(..., description="The original user request/question.")
    retrieved_content: str = Field(..., description="The retrieved content that needs to be pruned.")


class ContextPruningTool(BaseTool):
    name: str = "context_pruning_tool"
    description: str = (
        "Prunes retrieved content to extract only information relevant to the user's request. "
        "This tool removes irrelevant information, keeping only facts, data, and examples "
        "that directly answer the user's question. Use this after retrieving content to "
        "reduce token usage and improve response quality."
    )
    args_schema: Type[BaseModel] = ContextPruningInput

    def _run(self, user_request: str, retrieved_content: str) -> str:
        """Prune the retrieved content to focus on relevant information."""
        try:
            pruning_llm = _get_pruning_llm()
            
            pruning_prompt = f"""You are an expert at extracting relevant information from documents.

Your task: Analyze the provided document and extract ONLY the information that directly answers or supports the user's specific request. Remove all irrelevant content.

User's Request: {user_request}

Instructions for pruning:
1. Keep information that directly addresses the user's question
2. Preserve key facts, data, and examples that support the answer
3. Remove tangential discussions, unrelated topics, and excessive background
4. Maintain the logical flow and context of relevant information
5. If multiple subtopics are discussed, focus only on those relevant to the request
6. Preserve important quotes, statistics, and research findings when relevant

Return the pruned content in a clear, concise format that maintains readability while focusing solely on what's needed to answer the user's request."""
            
            messages = [
                {"role": "system", "content": pruning_prompt},
                {"role": "user", "content": retrieved_content}
            ]
            
            response = pruning_llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"Error during context pruning: {str(e)}. Returning original content.\n\n{retrieved_content}"
