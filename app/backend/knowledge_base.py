def create_knowledge_base(  
    source,  
    vector_db=None,  
    db_url="postgresql+psycopg://agno:agno@localhost:6024/agno",  
    table_name="knowledge_base",  
    embedder=None,  
    recreate=False,  
    chunk=False,  
    proxy=None  
):  
    """  
    Create a knowledge base from PDF files or URLs.  
      
    Args:  
        source (str or list): Path to PDF file/directory or list of PDF URLs  
        vector_db (VectorDb, optional): Vector database instance. If None, creates a PgVector instance.  
        db_url (str, optional): Database URL for vector storage.  
        table_name (str, optional): Table name for vector storage.  
        embedder (Embedder, optional): Embedder instance. If None, uses default embedder.  
        recreate (bool, optional): Whether to recreate the knowledge base. Defaults to False.  
        chunk (bool, optional): Whether to chunk documents. Defaults to False.  
        proxy (str, optional): Proxy URL for URL requests. Defaults to None.  
          
    Returns:  
        AgentKnowledge: The created knowledge base  
    """  
    from pathlib import Path  
    import os  
      
    # Set up default vector database if not provided  
    if vector_db is None:  
        from agno.vectordb.pgvector import PgVector, SearchType  
          
        # Set up default embedder if not provided  
        if embedder is None:  
            # Try to use Azure OpenAI embedder if environment variables are set  
            from agno.embedder.google import GeminiEmbedder
            embedder = GeminiEmbedder()  
          
        vector_db = PgVector(  
            table_name=table_name,  
            db_url=db_url,  
            search_type=SearchType.hybrid,  
            embedder=embedder  
        )  
      
    # Determine if source is a path or URLs  
    is_url = False  
    if isinstance(source, list) and all(isinstance(item, str) and (item.startswith('http://') or item.startswith('https://')) for item in source):  
        is_url = True  
    elif isinstance(source, str) and (source.startswith('http://') or source.startswith('https://')):  
        is_url = True  
        source = [source]  # Convert single URL to list  
      
    # Create appropriate knowledge base  
    if is_url:  
        from agno.knowledge.pdf_url import PDFUrlKnowledgeBase  
        from agno.document.reader.pdf_reader import PDFUrlReader  
          
        knowledge_base = PDFUrlKnowledgeBase(  
            urls=source,  
            vector_db=vector_db,  
            reader=PDFUrlReader()
        )  
    else:  
        from agno.knowledge.pdf import PDFKnowledgeBase  
        from agno.document.reader.pdf_reader import PDFReader  
          
        knowledge_base = PDFKnowledgeBase(  
            path=source,  
            vector_db=vector_db,  
            reader=PDFReader()  
        )  
      
    # Load the knowledge base  (Comment out if documents are already loaded)
    knowledge_base.load(recreate=recreate)  
      
    return knowledge_base