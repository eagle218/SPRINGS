import os
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
            dotenv.load_dotenv("../dev.env")
            return os.getenv("GPT_TOKEN")
        except FileNotFoundError:
            print("Warning: .env file not found, falling back to environment variables.")

    def pdf_load(self):
        """Loads the PDF document."""
        pdf_loader = PyPDFLoader(self.pdf_path)
        documents = pdf_loader.load()
        return documents

    def split_text(self):
        """Splits the PDF text into chunks using RecursiveCharacterTextSplitter."""
        split_text = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = split_text.split_documents(self.pdf_load())
        return documents

    def vectorize(self):
        """Creates a vector representation of the text using Chroma and OpenAIEmbeddings."""
        documents = self.split_text()
        vectorDB = Chroma.from_documents(
            documents,
            embedding=OpenAIEmbeddings(openai_api_key=self.load_dotenv_safe()),
            persist_directory="./data"
        )
        vectorDB.persist()
        return vectorDB

    def retrieval_qa(self, query):
        """Answers a query using ConversationalRetrievalChain and handles conversation history."""
        api_key = self.load_dotenv_safe()

        vectorDB = self.vectorize()
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.8, model_name="gpt-4", openai_api_key=api_key),
            retriever=vectorDB.as_retriever(search_kwargs={'k': 7}),
            return_source_documents=True
        )
        chat_history = []
        answer = qa_chain({"question": query, "chat_history": chat_history})
        chat_history.append((query, answer["answer"]))

        return answer["answer"]

    def run(self):
        """Runs the QA bot in an interactive loop."""

        print("QA bot based on your pdf file data. Type 'exit' to end conversation")

        while True:
            query = input("Your query: ")
            if query.lower().__contains__("exit"):
                return
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.retrieval_qa(query)
            print(result)
            
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QABot")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    args = parser.parse_args()

    bot = QABot(pdf_path=args.pdf_path)
    bot.run()
