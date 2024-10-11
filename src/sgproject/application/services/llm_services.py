# Business logic services
import re
import json
import torch
import pprint
import os
import shutil
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser


# Core business logic functions
def create_model(llm_model_name, embedding_model_name):
    # Initialization logic (embedding, LLM, etc.)
    # define global variables
    global embedding, llm_chain, gemma_llm, output_parser, use_llm_global, ner_pipeline

    # initialize the model/s
    models_dir_path = "data/models/"
    
    # TODO: Remove those when you put the model in the right place
    models_dir_path = "/home/sglbl/deduce/idbox/models/"

    embedding_path = models_dir_path + embedding_model_name

    # Load the embedding model
    model_kwargs = {"device": "cuda"} if torch.cuda.is_available() else {}
    
    if "nomic" in embedding_path:
        model_kwargs.update({"trust_remote_code": True})
    embedding = HuggingFaceEmbeddings(model_name=embedding_path, model_kwargs=model_kwargs)

    print(f"\nUsing {os.path.basename(embedding_path)} (embedding model)", end=" ")

    model_path = models_dir_path + llm_model_name
    tokenizer_path = models_dir_path + "gemma_tokenizer"
    
    print(f"and {os.path.basename(model_path)} (LLM)")

    # Model configs
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=False,
    )
    
    # TODO: Remove those when you put the model in the right place

    # Load model
    model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, do_sample=True, 
                                                device_map="auto", hidden_activation="gelu_pytorch_tanh", trust_remote_code=True) # .eval()
    # Load tokenizer
    tokenizer = tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Create pipeline for text generation from model and tokenizer
    text_generation_pipeline = pipeline(
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
        task="text-generation",
        temperature=0.2,
        max_new_tokens=300,
        eos_token_id=tokenizer.eos_token_id,
    )

    # Create llm from pipeline
    gemma_llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

    # Instruction: Answer the question based on the following context: 
    prompt_template = """
    Answer user's question:
    {context}

    Question:
    {question} 
    """
    
    # prompt_template = """
    # In the dict, there are Parques eólicos (Wind farms) from different cities, in a wind farm there are Aerogeneradors, and in the Aerogeneradors there are turbines. 
    # Each turbine has a temperature, energy, and a sensor label. User is going to ask to find the right label value. 
    # You will answer based on that information. For example if user asks for turbina label of number 4 of Burgos city, you will answer as BURGOS_AERO4_TURBINA.
    # {context}

    # Question:
    # {question} 
    # """

    # from langchain.output_parsers import CommaSeparatedListOutputParser, StructuredOutputParser, ResponseSchema
    # # ** TRYING OUTPUT PARSERS **
    # output_parser = CommaSeparatedListOutputParser()
    
    # response_schemas = [
    #     ResponseSchema(name="answer", description="answer to the user's question"),
    #     ResponseSchema(
    #         name="source",
    #         description="source used to answer the user's question is a json",
    #     ),
    # ]
    # output_parser = StructuredOutputParser.from_response_schemas(response_schemas)  
    
    # format_instructions = output_parser.get_format_instructions()

    # Create prompt from prompt template 
    prompt = PromptTemplate(
        input_variables=["context", "question"], #, "query"],
        template=prompt_template,
        # partial_variables={"format_instructions": format_instructions}
    )
    
    # Create llm chain 
    llm_chain = LLMChain(llm=gemma_llm, prompt=prompt) #, output_parser=output_parser)    
    
    # Checking if GPU is available
    if torch.cuda.is_available():
        print(f"\nGPU is available. Using GPU: {torch.cuda.get_device_name(0)}\n")
    else:
        print("\nGPU is not available.")
        
    # return llm_chain, embedding


def refresh_db():
    # remove content of 'data/chroma_data/'
    db_dir = "./data/chroma_data"
    if os.path.exists(db_dir):
        for file in os.listdir(db_dir):
            # if its a folder remove it as well
            if os.path.isdir(os.path.join(db_dir, file)):
                shutil.rmtree(os.path.join(db_dir, file))
            else:
                os.remove(os.path.join(db_dir, file))
        

def ask_to_model(query):
    # Main function to handle query and generate responses
    # This function calls the function (endpoint) we want to use
    # try:
        print(f"Query: {query}")
        file_directory = "data/docs/"
        # copy uploaded file to file_directory if exists
        if query.get("files"):
            source_file_path = query["files"][0]
            # Extract the filename from the full path
            filename = os.path.basename(source_file_path)
            # Define the destination path
            destination_file_path = os.path.join(file_directory, filename)

            # Copy the file to the destination directory
            shutil.copy2(source_file_path, destination_file_path)
        
        data = DirectoryLoader(file_directory, show_progress=True, silent_errors=True, loader_kwargs={f'text_content': False}).load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1500,
            chunk_overlap = 150
        )
        splitted_data = text_splitter.split_documents(data)
        
        # all_jsons = [os.path.splitext(f)[0] for f in os.listdir("./data/input") if f.endswith(".json")]
        # # all_jsons = ['Aero']
        # all_splitted_data = []


        # for json_key in all_jsons:
        #     # data = DirectoryLoader("data/input/", show_progress=True, loader_cls=JSONLoader, 
        #     #                     silent_errors=True, glob='**/*.json', loader_kwargs={f'jq_schema':f'.["{json_key}"][]', 'text_content': False}).load()
        #     # data = JSONLoader(f"data/input/{json_key}.json", jq_schema=f'.["{json_key}"][]', text_content=False).load()   # data = CSVLoader("data/input/Aero.csv").load()
        #     data = JSONLoader(f"./data/ProcessedData/merged_output.json", is_content_key_jq_parsable=True, jq_schema=f'.["{json_key}"][]', 
        #                       text_content=False).load()   # data = CSVLoader("data/input/Aero.csv").load()

        #     text_splitter = RecursiveCharacterTextSplitter(
        #         chunk_size = 5000,
        #         chunk_overlap = 150
        #     )
        #     all_splitted_data.append(text_splitter.split_documents(data))
        # splitted_data = sum(all_splitted_data, []) # flatten the list of lists
        
        print(f"{len(splitted_data) = }")
        
        db_index_vector_store = Chroma.from_documents(documents=splitted_data, embedding=embedding, persist_directory="data/chroma_data")    
        # all_content_combinations, unique_label_len = divide_question(query_text)
        llm_ans = llm_answer(db_index_vector_store, query)
        return llm_ans
    
    # except Exception as e:
    #     print(f"Error; ¡Something went wrong!: {e}")
    #     return ["Consult to developer: " + str(e)]


def llm_answer(db_index_vector_store, query):
    # Logic for LLM-based answer generation
    # ** Building the Retrieval System **
    # Retrieve and generate using the relevant snippets of the blog
    global llm_chain, gemma_llm, use_llm_global
    retriever = db_index_vector_store.as_retriever()
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = ( 
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | llm_chain  # | prompt | gemma_llm | StrOutputParser()
    )
    
    qa = RetrievalQA.from_chain_type(
        llm=gemma_llm,
        chain_type="stuff",
        retriever=retriever,
    )
    qa_res = qa.invoke(query["text"])
    # print(f"QA response: {qa_res}")

    response = rag_chain.invoke(query["text"])
    # print(f"LLM Model response: {response}")

    answer_match = re.search(r'Answer:\s*(.*)', response["text"])
    
    if answer_match is not None:
        # check if its jsonable
        try:
            response = json.loads(answer_match.group(1))
            response = pprint.pformat(response)
        except json.JSONDecodeError:
            response = answer_match.group(1)
    else:
        response = response["text"]
    # print(f"LLM Model response: {response}")
    return [response] 
