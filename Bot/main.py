import os
import sys
import dotenv
import argparse
import warnings
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain

class QABot:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def load_dotenv_safe(self):
        """Loads environment variables securely."""
        try:
            dotenv.load_dotenv("dev.env")
            return os.getenv("GPT_TOKEN")
        except FileNotFoundError:
            print("Warning: .env file not found, falling back to environment variables.")

    def pdf_load(self):
        """Loads the PDF document."""
        pdf_loader = PyPDFLoader(self.pdf_path)
        documents = pdf_loader.load()
        return documents

    def split_text(self):
        split_text = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=100)
        documents = split_text.split_documents(self.pdf_load())
        return documents

    def vectorize(self):
        documents = self.split_text()
        vectorDB = Chroma.from_documents(
            documents,
            embedding=OpenAIEmbeddings(openai_api_key=self.load_dotenv_safe()),
            persist_directory="./data"
        )
        vectorDB.persist()
        return vectorDB

    def initialize_qa_chain(self, db, api_key):
        api_key = api_key
        vectorDB = db
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.8, model_name="gpt-4", openai_api_key=api_key),
            retriever=vectorDB.as_retriever(search_kwargs={'k': 7}),
            return_source_documents=True
        )
        return qa_chain

    def retrieval_qa(self, query, qa_chain_object):
        chat_history = []
        answer = qa_chain_object({"question": query, "chat_history": chat_history})
        chat_history.append((query, answer["answer"]))

        return answer["answer"]

    def run(self, api_key, qa_chain_object):
        print("QA bot based on your pdf file data. Type 'exit' to end conversation")

        while True:
            query = input("Your query: ")
            if query.lower().__contains__("exit"):
                return
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.retrieval_qa(query, qa_chain_object=qa_chain_object)
            print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QABot")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    args = parser.parse_args()

    bot = QABot(pdf_path=args.pdf_path)
    db = bot.vectorize()
    api_key = bot.load_dotenv_safe()
    qa_chain_object = bot.initialize_qa_chain(db, api_key)

    bot.run(api_key, qa_chain_object)
    