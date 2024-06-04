# (c) 2020-2024 Data Santander, SL.
# File: Tutorial_02.py
# Purpose: Ingest local PDFs and save the generated index files locally for faster re-load.
# ver 01 - Tue 04 June 2024 - Jose.Lacal@DataSDR.com
#
"""
Requirements:
* Download the GitHub repository: https://github.com/JLacal/local-llm
* Follow configuration instructions defined in the file https://github.com/JLacal/local-llm/blob/main/TrialTwin_Local_LLM.pdf
* Download the sample PDFs here: https://github.com/JLacal/local-llm/blob/main/ClinicalTrials_gov_10_PDFs.zip
* Open a command line window (Terminal / Powershell).
* Activate the virtual environment.
* Then type: "python3 Tutorial_02.py"

The first time you process a set of PDFs the script will generate the index files.
Any other time you run the script it will re-load the previously-generated index files.
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

# Tutorial: location of PDF files you want to process.
# Download and extract the PDFs from https://github.com/JLacal/local-llm/blob/main/ClinicalTrials_gov_10_PDFs.zip here.
CT_DATA_DIR = "/Users/server/Downloads/test/_data"
# Tutorial: location of index files.
CT_INDEX_DIR = "/Users/server/Downloads/test/_index"
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

"""
These are the titles of the PDFs you downloaded above. Use this material to craft better questions below.


Statistical Analysis Plan
A Monocentric, Open-Label, Proof of Concept Study to Evaluate the
Safety and Efficacy of NTZ at 500mg Twice Daily on Collagen Turnover
in Plasma in NASH Patients with Fibrosis Stage 2 or 3.
NCT Number: 03656068
Unique Protocol ID: NTZ-218-1
Version Date : 09 April 2020


Use of a Telehealth Intervention to Decrease Readmissions in Cirrhosis: A Randomized Controlled Trial
NCT03969186
20 June 2019


Title :Efficacy and Safety of Nadroparin Calcium-Warfarin Sequential
Anticoagulation in Portal Vein Thrombosis in Cirrhotic Patients：A
Randomized Controlled Trial
NCT number: NCT04173429
Date of the Document:2020-7-3


TITLE:
The effect of probiotics in non-alcoholic fatty liver disease and
steatohepatitis measured by transient elastography
NCT 04175392
Approval date: 04/07/2021
Study Protocol and Statistical Analysis Plan


Protocol & Statistical Analysis Plan for:
Increasing Surveillance Rates for Hepatocellular Carcinoma Among Cirrhotic Patients
University of Pennsylvania
Dr. Shivan Mehta
NCT#04248816
v. 7/20/21
Approved: 7/23/21


Study Title: COMPARISON THE SEROCONVERSION RATE BETWEEN TWO-DOSE AND THREE-
DOSE REGIMENS OF HEPLISAV-B AMONG PATIENTS WITH CIRRHOSIS, A RANDOMIZED
CONTROL PROSPECTIVE STUDY.


Study Title: Comparison the seroconversion rate between two-dose and three-dose regimens of Heplisav B among patients with cirrhosis, a randomized-control prospective study.


Official Title: Safety and feasibility of Early Oral Nutrition after Endoscopic Treatment for Patients with Liver Cirrhosis: A Historical-prospective, Comparative Effectiveness study
NCT number: NCT04823780 Document date: September 1, 2020


Protocol: Collection of Blood Products for Use in the Development and Validation
of Point-of-Care In Vitro Diagnostic Liver Function Test Devices
Study GKD001
NCT # Not Yet Assigned
IRB Approved Date 6/23/2022
"""

# - - - - -
# Imports Section
import time
start_time = time.time()
#
import os.path
#
# Tutorial: import core LlamaIndex libraries needed for this file to run properly.
# Notice a few new imports compared to Tutorial_01.py
from llama_index.core import (
    Document,
    load_index_from_storage,
	Settings,
	SimpleDirectoryReader,
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
# Tutorial: 
from llama_index.readers.database import DatabaseReader
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

# Check if index already exists
if not os.path.exists(CT_INDEX_DIR):
	os.makedirs(CT_INDEX_DIR)
	documents = SimpleDirectoryReader(CT_DATA_DIR).load_data()
	#
	index = VectorStoreIndex.from_documents(
	    documents,
	)
	#
	index.storage_context.persist(persist_dir=CT_INDEX_DIR)
	print("Index stored in directory [%s]\n\n" % (CT_INDEX_DIR))
	#
else:
	# Load existing index:
	print("Loading index from directory [%s]\n\n" % (CT_INDEX_DIR))
	storage_context = StorageContext.from_defaults(persist_dir=CT_INDEX_DIR)
	index = load_index_from_storage(storage_context)
	print("Index loaded.\n\n")
#
# Tutorial: now we'll ask the LLM questions regarding the PDFs we loaded.
print("\n\n\n= = = Inference = = =")
# Tutorial: create a query engine on the index object.
query_engine= index.as_query_engine()


#
# Tutorial: ask questions to the query engine.
response_01 = query_engine.query("Describe the protocol about Thrombosis?")
print(response_01, "\n")
#
response_02 = query_engine.query("What do you know about elastography from the context?")
print(response_02, "\n")
# Tutorial: 
response_03 = query_engine.query("What do you know about Heplisav B from the context?")
print(response_03, "\n")


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
Thrombotic material presence within vessels was defined as complete or greater than 90% and partial or less than 90%. Complete thrombosis was characterized by equal to or greater than 90% thrombotic material presence, while partial thrombosis was defined as less than 90% thrombotic material presence. Thrombus progression was described as more than 30% increase in thrombus dimension or extension to unaffected segments of the splenoportomesenteric axis.
I don't have any information about elastography in this context. The provided text only mentions Child-Pugh score, MELD score, hemat emesis, melena, epistaxis, injection-site hemorrhage, and other bleeding events, but not elastography.
According to the provided context, Heplisav-B is a vaccine that uses a synthetic cytosine phosphoguanine oligonucleotide derived from bacterial DNA. It stimulates the immune system through activation of the toll-like receptor 9 pathway, which induces production of cytokines such as interleukin-12 and interferon-alpha. The vaccine has been shown to induce higher immunity in healthy individuals compared to conventional vaccines. Additionally, the vaccine titer should be checked 8 to 12 weeks after administration of the vaccination series, with good responders having an anti-HBs titer ≥ 100 mIU/ml, poor responders having an anti-HBs titer between 10 and 99 mIU/ml, and nonresponders having an anti-HBs titer < 10 mIU/ml.
"""


# = = = = = HOMEWORK = = = = =
"""
01. Change the model name in CT_MODEL_NAME for each of the LLMs you downloaded, and re-run the code.
Compare the results of each model over the exact same content.
>> Spoiler alert: LLMs lie! <<


02. Test with your own PDFs:
* Delete the PDFs in the CT_DATA_DIR directory.
* Add your own, internal PDFs here.
* Delete the CT_INDEX_DIR directory.
* Re-run the script.
"""