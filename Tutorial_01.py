# (c) 2020-2024 Data Santander, SL.
# File: Tutorial_01.py
# Purpose: Step by step description of concepts related to augmenting a base LLM.
# This is a full Minimum Working Demo.
# ver 01 - Tue 04 June 2024 - Jose.Lacal@DataSDR.com
#
"""
Requirements:
* Download the GitHub repository: https://github.com/JLacal/local-llm
* Follow configuration instructions defined in the file https://github.com/JLacal/local-llm/blob/main/TrialTwin_Local_LLM.pdf
* Open a command line window (Terminal / Powershell).
* Activate the virtual environment.
* Then type: "python3 Tutorial_01.py"
"""

"""
Common errors:

Message:
	httpx.HTTPStatusError: Client error '404 Not Found' for url 'http://localhost:11434/api/chat'
Reason:
	The model name you selected has not been downloaded to your local computer.
"""

# Tutorial: use this global variable to debug the code below.
CT_DEBUG = 0

#
# Tutorial: increase the timeout when running on low-powered hardware.
CT_REQUEST_TIMEOUT = 360.0

# Tutorial: Here you assign a model name to a global variable.
CT_MODEL_NAME = ["llama3"]
"""
Choose from these possible model names. 
!! MAKE SURE you have downloaded the model first, using "ollama pull <ModelName>""

	codegemma
	command-r
	command-r-plus
	duckdb-nsql
	gemma:2b
	gemma:7b
	llama-pro
	llama3
	llama3-chatqa
	llama3-gradient
	llama3:70b
	llama3:70b-text
	llama3:text
	meditron
	medllama2
	orca-mini
	phi3:medium
	phi3:mini
	tinyllama
	wizardlm2:7b
	wizardlm2:8x22b
"""
# Tutorial: Here you select the embedding model you want to use.
CT_EMBEDDING_MODEL = ["nomic-embed-text"]
"""
!! MAKE SURE you have downloaded the embedding model first: "ollama pull nomic-embed-text"
"""

# - - - - -
# Imports Section
import time
start_time = time.time()
#
# Tutorial: import core LlamaIndex libraries needed for this file to run properly.
from llama_index.core import (
    Document,
	Settings,
	StorageContext,
    SummaryIndex,
	VectorStoreIndex,
)
# Tutorial: import LlamaIndex libraries needed to handle Document definitions.
from llama_index.core.schema import Document, MetadataMode
#
# Tutorial: import LlamaIndex libraries needed to interface with Ollama.
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
#
# Tutorial: call the specified embedding model.
# An "embedding model" turns raw data into tokens ready to eb processed.
Settings.embed_model = OllamaEmbedding(model_name=CT_EMBEDDING_MODEL[0])
#
# Tutorial: configure Ollama with the desired model name, and define a request timeout.
Settings.llm = Ollama(model=CT_MODEL_NAME[0], request_timeout=CT_REQUEST_TIMEOUT)
#
# Tutorial: initialize an index object.
index = SummaryIndex([])
#
# Tutorial: manually define the content of a single Document instance.
document = Document(
	text="Full text of application document for melanoma goes here. Only suitable for children over 10 years of age.",
	metadata={
		"filename": "FDA Applications",
		"category": "US - FDA",
		"author": "TrialTwin",
        "sponsor": "Acme, Inc.",        
        "label": "melanoma",
        "date": "2024-02-01",
		},
	excluded_llm_metadata_keys=["file_name"],
	metadata_separator="::",
	metadata_template="{key}=>{value}",
	text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
)
# Tutorial: manually assign an ID to the Document created above.
document.doc_id = "My new document id!"
#
# Tutorial: actually insert the Document into the index.
index.insert(document)
#
# Tutorial: for debugging purposes only.
if CT_DEBUG == 1:
	print(
		"\nThe LLM sees this: \n",
		document.get_content(metadata_mode=MetadataMode.LLM),
	)
	# Tutorial: for debugging purposes only.
	print(
		"\nThe Embedding model sees this: \n",
		document.get_content(metadata_mode=MetadataMode.EMBED),
	)

# Tutorial: uncomment for debugging purposes only.
if CT_DEBUG == 2:
	print(index.ref_doc_info)
#
# Tutorial: now we'll ask the LLM questions regarding the Document we created manually.
print("\n\n\n= = = Inference = = =")
# Tutorial: create a query engine on the index object.
query_engine= index.as_query_engine()
#
# Tutorial: ask questions to the query engine.
response_01 = query_engine.query("When was the melanoma drug approved?")
print(response_01)
#
response_02 = query_engine.query("Who is the spponsor for the melanoma drug?")
print(response_02)
# Tutorial: 
response_03 = query_engine.query("Are there any age restrictions on the melanoma drug?")
print(response_03)


#
print ("\n\n= = = = =\nThis is the end\nBeautiful friend\nThis is the end\nMy only friend, the end.  [The Doors, of course]")
print("--- Runtime: %s seconds ---\n" % (time.time() - start_time))

"""
Expected response with model "llama2":

Inference:
The approval date for the melanoma drug is February 1st, 2024, according to the application document provided in the context information.
The sponsor for the melanoma drug is Acme, Inc.
The answer to your question cannot be directly provided based on the given context information. The context only provides information about the FDA application for a melanoma drug and does not provide any age restrictions related to the drug. Therefore, I cannot provide an answer to your query based solely on the given context.



Expected response with model "llama3":

Inference:
I'm happy to help! According to the provided information, the date is 2024-02-01.
Acme, Inc.
According to the provided information, the content is only suitable for children over 10 years of age. This suggests that there might be an implicit or explicit age restriction for the melanoma drug.

"""


# = = = = = HOMEWORK = = = = =
"""
01. Change the model name in CT_MODEL_NAME for each of the LLMs you downloaded, and re-run the code.
Compare the results of each model over the exact same content.
>> Spoiler alert: LLMs lie! <<


02. Choose a single model (I recommend "llama2"). Now change the content inside 
	document = Document(..

and change the questions in 
	response = query_engine.query

"""