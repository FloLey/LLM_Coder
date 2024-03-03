from langchain_openai import ChatOpenAI
LLM = ChatOpenAI(temperature=0, model_name="gpt-4-turbo-preview", streaming=True)