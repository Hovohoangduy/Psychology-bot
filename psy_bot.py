import time
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import FAISS

# Cau hinh
model_file = "pre_models/vinallama-2.7b-chat_q5_0.gguf"
vector_db_path = "vectorstores/db_faiss"

# Load LLM
def load_llm(model_file):
    llm = CTransformers(
        model=model_file,
        model_type="llama",
        max_new_tokens=256,
        temperature=0.01
    )
    return llm

# Tao prompt template
def creat_prompt(template):
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    return prompt

# Tao simple chain
def create_qa_chain(prompt, llm, db):
    llm_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}, max_tokens_limit=256),
        return_source_documents=False,
        chain_type_kwargs={'prompt': prompt}
    )
    return llm_chain

# Read tu VectorDB
def read_vectors_db():
    # Embedding
    embedding_model = GPT4AllEmbeddings(model_file="pre_models/all-MiniLM-L6-v2-f16.gguf")
    db = FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)
    return db

# Bat dau thu nghiem
db = read_vectors_db()
llm = load_llm(model_file)

# Tao Prompt
template = """<|im_start|>system\nSử dụng thông tin sau đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời\n
    {context}<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant"""
prompt = creat_prompt(template)

llm_chain = create_qa_chain(prompt, llm, db)

# Chay chain và đo thời gian
question = "Dấu hiệu và triệu chứng sang chấn thường gặp ở người trưởng thành,trẻ em và nhóm yếu thế sau dịch COVID-19?"
start_time = time.time()  # Ghi nhận thời điểm bắt đầu
response = llm_chain.invoke({"query": question})
end_time = time.time()  # Ghi nhận thời điểm kết thúc

# Tính thời gian
elapsed_time = end_time - start_time
print(f"Câu trả lời: {response}")
print(f"Thời gian sinh ra câu trả lời: {elapsed_time:.2f} giây")