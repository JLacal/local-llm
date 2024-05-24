
ClinicalTrials.gov 

SELECT 
		nct_id
		, nlm_download_date_description
		, study_first_submitted_date
		, results_first_submitted_date
		, disposition_first_submitted_date
		, last_update_submitted_date
		, study_first_submitted_qc_date
		, study_first_posted_date
		, study_first_posted_date_type
		, results_first_submitted_qc_date
		, results_first_posted_date
		, results_first_posted_date_type
		, disposition_first_submitted_qc_date
		, disposition_first_posted_date
		, disposition_first_posted_date_type
		, last_update_submitted_qc_date
		, last_update_posted_date
		, last_update_posted_date_type
		, start_month_year
		, start_date_type
		, start_date
		, verification_month_year
		, verification_date
		, completion_month_year
		, completion_date_type
		, completion_date
		, primary_completion_month_year
		, primary_completion_date_type
		, primary_completion_date
		, target_duration
		, study_type
		, acronym
		, baseline_population
		, brief_title
		, official_title
		, overall_status
		, last_known_status
		, phase
		, enrollment
		, enrollment_type
		, source
		, limitations_and_caveats
		, number_of_arms
		, number_of_groups
		, why_stopped
		, has_expanded_access
		, expanded_access_type_individual
		, expanded_access_type_intermediate
		, expanded_access_type_treatment
		, has_dmc
		, is_fda_regulated_drug
		, is_fda_regulated_device
		, is_unapproved_device
		, is_ppsd
		, is_us_export
		, biospec_retention
		, biospec_description
		, ipd_time_frame
		, ipd_access_criteria
		, ipd_url
		, plan_to_share_ipd
		, plan_to_share_ipd_description
		, created_at
		, updated_at
		, source_class
		, delayed_posting
		, expanded_access_nctid
		, expanded_access_status_for_nctid
		, fdaaa801_violation
		, baseline_type_units_analyzed
		, nihpo_pdf_file_contents
		, nihpo_pdf_file_number_pages
		, nihpo_pdf_document_type
		FROM us_clinical_trials_nihpo
		WHERE nihpo_pdf_file_contents IS NOT NULL


Drugs@FDA:

SELECT 
	DISTINCT(applicationdocs.applno)
	, applicationdocs.item_id
	, applicationdocs.applicationdocsid
	, applicationdocs.applicationdocstypeid
	, applicationdocs.submissiontype
	, applicationdocs.submissionno
	, applicationdocs.applicationdocstitle
	, applicationdocs.applicationdocsdate
	, applicationdocs.nihpo_pdf_file_page_count
	, applicationdocs.nihpo_pdf_file_contents
	, products.form
	, products.strength
	, products.referencedrug
	, products.drugname
	, products.activeingredient
	, products.referencestandard
	, applications.appltype
	, applications.sponsorname
	--
	FROM fda_drugsatfda_applicationdocs applicationdocs 
		LEFT JOIN fda_drugsatfda_products products ON applicationdocs.applno = products.applno
		LEFT JOIN fda_drugsatfda_applications applications ON applicationdocs.applno = applications.applno
	WHERE applicationdocs.nihpo_pdf_file_contents IS NOT NULL
