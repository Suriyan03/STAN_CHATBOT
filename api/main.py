# File: api/main.py

import os
import redis
import json
from fastapi import FastAPI
from dotenv import load_dotenv
from api.debug import router as debug_router

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, messages_from_dict, messages_to_dict

from api.models import ChatRequest, ChatResponse
from core.constants import SYSTEM_PROMPT

# Import the new, simplified vector_store object
from persistence.vector_store import vector_store

load_dotenv()
app = FastAPI(title="Human-Like Chatbot API (Modern RAG)")

app.include_router(debug_router, prefix="/api/v1/debug")


# --- SERVICE CONNECTIONS ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
llm = ChatGoogleGenerativeAI(model="models/gemini-pro-latest", temperature=0.7)
summarizer_llm = ChatGoogleGenerativeAI(model="models/gemini-pro-latest", temperature=0.2)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_lyra(request: ChatRequest):
    redis_key = f"history:{request.user_id}"

    try:
        # Retrieve SHORT-TERM memory from Redis
        stored_history = redis_client.get(redis_key)
        user_history = messages_from_dict(json.loads(stored_history)) if stored_history else []

        # Retrieve LONG-TERM memories using the LangChain retriever interface
        retriever = vector_store.as_retriever(search_kwargs={'filter': {'user_id': request.user_id}})
        
        # --- THE FIX IS HERE ---
        # The modern method to get documents is .invoke() not .get_relevant_documents()
        relevant_docs = retriever.invoke(request.message)
        
        memory_context = "\n".join([doc.page_content for doc in relevant_docs])
        
        dynamic_prompt = f"""{SYSTEM_PROMPT}

# Conversation Context from Your Memory:
(You remember the following things about this user. Use this information to enrich the conversation and make it personal. But don't explicitly say "I remember...")
{memory_context}
"""
        
        messages = [SystemMessage(content=dynamic_prompt)] + user_history + [HumanMessage(content=request.message)]
        response = llm.invoke(messages)
        ai_reply = response.content

        # Update SHORT-TERM memory in Redis
        updated_history = user_history + [HumanMessage(content=request.message), AIMessage(content=ai_reply)]
        redis_client.set(redis_key, json.dumps(messages_to_dict(updated_history)))

        # Decide whether to create a new LONG-TERM memory
        if len(updated_history) % 4 == 0 and len(updated_history) > 0:
            summary_prompt = f"""Concisely summarize key facts or user preferences from the following conversation: {updated_history}"""
            summary = summarizer_llm.invoke(summary_prompt).content
            
            # Add the summary to ChromaDB using the LangChain interface
            vector_store.add_texts(
                texts=[summary],
                metadatas=[{'user_id': request.user_id}]
            )
            print(f"Added new long-term memory for user '{request.user_id}'")

        return ChatResponse(reply=ai_reply)

    except Exception as e:
        print(f"An error occurred: {e}")
        return ChatResponse(reply=f"An error occurred: {str(e)}")