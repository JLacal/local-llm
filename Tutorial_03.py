# (c) 2020-2024 Data Santander, SL.
# File: Tutorial_03.py
# Purpose: Ingest data stored in local SQLite3 files, build indices, and then conduct searches.
# ver 01 - Tue 04 June 2024 - Jose.Lacal@DataSDR.com
#
"""
Requirements:
* Download the GitHub repository: https://github.com/JLacal/local-llm
* Follow configuration instructions defined in the file https://github.com/JLacal/local-llm/blob/main/TrialTwin_Local_LLM.pdf
* Download the sample SQLite3 files listed bbelow.
* Open a command line window (Terminal / Powershell).
* Activate the virtual environment.
* Make sure Ollama is running! "ollama serve" or launch the application.
* Then type: "python3 Tutorial_03.py"


The first time you process a set of SQLite3 files:
	Uncomment this lines:
		func_datasdr_unzip_files(CT_SQLITE3_DIRECTORY)
		func_datasdr_generate_indices(CT_SPONSORS_NAME, CT_SQLITE3_DIRECTORY)

After the index files are created, comment both lines.

Now you can add your own questions inside 
	func_datasdr_ask_questions(..)


Available SQLite3 files:
Each file contains details of clinical trials sponsored by each company. Each SQLite3 file also contains the full text of individual Protocols, Statistical Plans ("SAP") and ICF ("Individual Consent Forms").
")")
	Abbott :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Abbott.sqlite3.zip
	Abbvie :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Abbvie.sqlite3.zip
	AstraZeneca :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_AstraZeneca.sqlite3.zip
	Bayer :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Bayer.sqlite3.zip
	Bristol Myers Squibb :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Bristol_Myers_Squibb.sqlite3.zip
	Johnson & Johnson :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Johnson_Johnson.sqlite3.zip
	Pfizer :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Pfizer.sqlite3.zip
	Roche :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Roche.sqlite3.zip
	Sanofi :: https://github.com/JLacal/local-llm/blob/main/TrialTwin_Sanofi.sqlite3.zip
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

# Tutorial: list of SQLite3 file names by sponsor. Adjust based on the names of the SQLite3 files you actually downloaded.
CT_SPONSORS_NAME = ['Abbott', 'Abbvie', 'AstraZeneca', 'Bayer', 'Bristol_Myers_Squibb', 'Johnson_Johnson', 'Pfizer', 'Roche', 'Sanofi']
#
# Tutorial: start with a few records, say 10. Then slowly increase the number of records, based on your hardware's capabilities.
CT_LIMIT_RECORDS = 10
# Tutorial: adjust to fit your local configuration.
CT_SQLITE3_DIRECTORY = "/Users/server/Downloads/test/_Datafiles/"
#
# Tutorial: location of SQLite3 files you want to process.
# Download and extract the SQLite3 files listed above.
CT_DATA_DIR = "/Users/server/Downloads/test/_data"
# Tutorial: location of index files.
CT_INDEX_DIR = "/Users/server/Downloads/test/_index"
#
# Tutorial: increase the timeout when running on low-powered hardware.
CT_REQUEST_TIMEOUT = 360.0

# Tutorial: Here you assign a model name to a global variable.
CT_MODEL_NAME = ["llama2"]
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
import os
import sys
from zipfile import ZipFile
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
# Tutorial: this library allows the Python code to access data stored in databases.
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
CT_INDEX_DIR = os.path.join(CT_SQLITE3_DIRECTORY, "_index")
#
def func_datasdr_unzip_files(in_directory:str) -> int:
	"""
	This function unZIPs a directory full of ZIPped files.

	in_directory: str - Directory where ZIped files are located at.
	"""
	for root, dirs, files in os.walk(CT_SQLITE3_DIRECTORY):
		#
		full_filenames = [os.path.join(root, name) for name in files]
		for each_filename in full_filenames:
			if each_filename.endswith(".zip"):
				zfile = ZipFile(each_filename)
				zfile.extractall(CT_SQLITE3_DIRECTORY)
				zfile.close()
	#
	return 1
#
# Tutorial: now we open each SQLite3 file; retrieve records; and generate the corresponding index files:
def func_datasdr_generate_indices(in_sponsors_dict, in_sqlite_directory: str) -> int:
	"""
	This function generates sponsor-specific index for each SQLite3 file in the directory.

	in_sponsors_dict - Dictionary with names of sponsors.
	in_sqlite_directory: str - Directory where SQLite3 files are located at.
	"""
	for one_sponsor in in_sponsors_dict:
		# SQLite3:
		reader_DB = DatabaseReader(
			uri = "sqlite:///%sTrialTwin_%s.sqlite3" % (in_sqlite_directory, one_sponsor),
		)
		var_sponsor_index_directory = "%s_%s" % (in_sqlite_directory, one_sponsor)
		# Check if index already exists
		if not os.path.exists(var_sponsor_index_directory):
			os.makedirs(var_sponsor_index_directory)
			#
			print("\n\nRetrieve data from SQLite3 file for [%s]\n" % (one_sponsor))
			#
			documents_DB = reader_DB.load_data(
			 	query="SELECT nct_id, nlm_download_date_description, study_first_submitted_date, results_first_submitted_date, disposition_first_submitted_date, last_update_submitted_date, study_first_submitted_qc_date, study_first_posted_date, study_first_posted_date_type, results_first_submitted_qc_date, results_first_posted_date, results_first_posted_date_type, disposition_first_submitted_qc_date, disposition_first_posted_date, disposition_first_posted_date_type, last_update_submitted_qc_date, last_update_posted_date, last_update_posted_date_type, start_month_year, start_date_type, start_date, verification_month_year, verification_date, completion_month_year, completion_date_type, completion_date, primary_completion_month_year, primary_completion_date_type, primary_completion_date, target_duration, study_type, acronym, baseline_population, brief_title, official_title, overall_status, last_known_status, phase, enrollment, enrollment_type, source, limitations_and_caveats, number_of_arms, number_of_groups, why_stopped, has_expanded_access, expanded_access_type_individual, expanded_access_type_intermediate, expanded_access_type_treatment, has_dmc, is_fda_regulated_drug, is_fda_regulated_device, is_unapproved_device, is_ppsd, is_us_export, biospec_retention, biospec_description, ipd_time_frame, ipd_access_criteria, ipd_url, plan_to_share_ipd, plan_to_share_ipd_description, created_at, updated_at, source_class, delayed_posting, expanded_access_nctid, expanded_access_status_for_nctid, fdaaa801_violation, baseline_type_units_analyzed, datasdr_brief_summaries__description, datasdr_downcase_name_list, datasdr_baseline_counts__count, datasdr_baseline_counts__ctgov_group_code, datasdr_baseline_counts__result_group_id, datasdr_baseline_counts__scope, datasdr_baseline_counts__units, datasdr_code_biospec_retention, datasdr_code_enrollment_type, datasdr_code_expanded_access_status_for_nctid, datasdr_code_last_known_status, datasdr_code_overall_status, datasdr_code_phase, datasdr_code_plan_to_share_ipd, datasdr_code_source_class, datasdr_code_study_type, datasdr_pdf_file_contents, datasdr_pdf_file_number_pages, datasdr_pdf_document_type, lead_or_collaborator, name FROM %s ORDER BY nct_id ASC LIMIT %d;" % (one_sponsor, CT_LIMIT_RECORDS)
			)
			#
			print("Database results received.\nWill generate index in directory [%s]\n" % (var_sponsor_index_directory))
			#
			index_DB = VectorStoreIndex.from_documents(
				documents_DB,
				show_progress=True
				)
			#
			index_DB.storage_context.persist(persist_dir=var_sponsor_index_directory)
			print("Index stored in directory [%s]\n\n" % (var_sponsor_index_directory))
		#
	#
	return 1
#
#
# Tutorial: now we'll ask the LLM questions regarding the SQLite3 files we generated indices for.
def func_datasdr_ask_questions(in_sponsors_dict, in_sqlite_directory) -> int:
	"""
	This function will ask questions using the pre-generated index files.

	in_sponsors_dict - Dictionary with names of sponsors.
	in_sqlite_directory: str - Directory where SQLite3 files are located at.
	"""
	print("\n\n\n= = = Inference = = =")

	for one_sponsor in in_sponsors_dict:
		var_sponsor_index_directory = "%s_%s" % (in_sqlite_directory, one_sponsor)
		# Load existing index:
		print("\n\n= = = = = Sponsor: %s = = = = =\n" % (one_sponsor))
		print("Loading index from directory [%s]" % (var_sponsor_index_directory))
		storage_context = StorageContext.from_defaults(persist_dir=var_sponsor_index_directory)
		index = load_index_from_storage(storage_context)
		print("Index loaded.")
		#
		# Tutorial: create a query engine on the index object.
		query_engine= index.as_query_engine()
		#
		# Tutorial: now we ask the same question to all indices.
		#
		# Tutorial: ask questions to the query engine.
		response_01 = query_engine.query("How many studies has this sponsor conducted?")
		print(response_01, "\n")
		#
		response_02 = query_engine.query("How many studies of type 'Interventional'?")
		print(response_02, "\n")
		# 
		response_03 = query_engine.query("How many studies have an overall status of 'Completed'?")
		print(response_03, "\n")
		#
		return 1
#
#
if __name__ == "__main__":
	print ("\n\nStarting Tutorial_03.py\n\n")
	#
	# Tutorial: comment the following line if the ZIPped files have been extracted already:
	# func_datasdr_unzip_files(CT_SQLITE3_DIRECTORY)
	#
	# Tutorial: comment the following line if the SQLite3 files have been processed already:
	func_datasdr_generate_indices(CT_SPONSORS_NAME, CT_SQLITE3_DIRECTORY)
	#
	# Tutorial: ask questions.
	# func_datasdr_ask_questions(CT_SPONSORS_NAME, CT_SQLITE3_DIRECTORY)



print ("\n\n= = = = =\nThis is the end\nBeautiful friend\nThis is the end\nMy only friend, the end.  [The Doors, of course]")
print("--- Runtime: %s seconds ---\n" % (time.time() - start_time))

"""
Expected response with model "llama2" for "Abbott":

= = = = = Sponsor: Abbott = = = = =

Loading index from directory [/Users/server/Downloads/test/_Datafiles/_Abbott]
Index loaded.
Based on the provided context, it is not possible to determine how many studies the sponsor has conducted. The context does not provide any information about the number of studies conducted by the sponsor. Therefore, I cannot give a direct answer to the query. However, I can suggest that you consult the sponsor's website or other reliable sources for more information on their research activities and publications. 

Based on the provided context information, there are 10 studies listed in the Investigational Plan. 

Based on the provided context information, I cannot directly answer the query "How many studies have an overall status of 'Completed'?" as it would require me to reference the given context. Instead, I will provide a response that does not directly reference the context:

The number of studies with an overall status of 'Completed' can be determined by analyzing the context information provided. From the information given, there are 77 studies in total, and each study has a unique ID ranging from 1 to 77. Additionally, the context includes information about the status of each study, including whether it is 'Completed'.

To determine the number of completed studies, you can count the number of studies with an overall status of 'Completed' by analyzing the context information. The results of this analysis will provide the answer to your query. 






Expected response with model "llama3" for "Abbott":

= = = = = Sponsor: Abbott = = = = =

Loading index from directory [/Users/server/Downloads/test/_Datafiles/_Abbott]
Index loaded.
Based on the provided context information, it is not possible to determine how many studies this sponsor has conducted. The information does not contain any data or statistics related to the number of studies conducted by the sponsor. Therefore, I cannot provide a numerical answer to this query. 

Based on the provided context information, it appears that this is an Investigational Plan for a clinical study. The document does not explicitly indicate the number of studies of type "Interventional". However, given the content and structure of the plan, it can be inferred that this is likely a single study protocol, rather than multiple studies.

Therefore, the answer to the query would be: 1 

According to the provided data, there are 77 studies with a status code '(6&5,37,9( that indicates they have been completed. 

"""


# = = = = = HOMEWORK = = = = =
"""
01. Change the model name in CT_MODEL_NAME for each of the LLMs you downloaded, and re-run the code.
Compare the results of each model over the exact same content.
>> Spoiler alert: LLMs lie! <<


02. Test with your own SQLite files.
"""