from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader, PdfMerger
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI


def main():
    load_dotenv()
    st.set_page_config(
        page_title="Ask Faculty Senate Constitution, Bylaws and Administrative Faculty Committee Bylaws"
    )
    st.image("./UNLV-186.png", width=200)
    st.header("Faculty Senate AI Assistant 🤓", divider="rainbow")
    st.header(
        "Ask Faculty Senate Constitution, Bylaws and Administrative Faculty Committee Bylaws"
    )

    with open("./FS_Const_Bylaws_AFC_Bylaws.pdf", "rb") as f:
        st.download_button(
            "Download the Constitution, Bylaws and AFC Bylaws combined PDF",
            f,
            file_name="./FS_Const_Bylaws_AFC_Bylaws.pdf",
        )

    pdfs = [
        "./FacultySenateConstitution7-17.pdf",
        "./FacultySenateBylaws22.pdf",
        "./AFC By-Laws.pdf",
    ]

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("FS_Const_Bylaws_AFC_Bylaws.pdf")
    merger.close()

    pdf = "./FS_Const_Bylaws_AFC_Bylaws.pdf"

    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )

        chunks = text_splitter.split_text(text)

        # create embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        user_question = st.text_input("Type your question here:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)

            st.write(response)


if __name__ == "__main__":
    main()
