import json
from pydantic import BaseModel, Field, create_model
from typing import Any, Type, Optional, List, Literal

# --- Predefined Templates from Requirements ---
PREDEFINED_TEMPLATES = {
    "Study Details": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "title": "string",
        "publication_year": "string",
        "journal": "string",
        "volume": "string",
        "issue": "string",
        "page_number": "string",
        "study_name": "string",
        "linked_citation_id": "string",
        "full_paper_or_abstract": "string",
        "setting": "string",
        "study_design": "string",
        "phase": "string",
        "blinding": "string",
        "disease_type": "string",
        "disease_severity": "string",
        "disease_definition": "string",
        "icd_codes": "string",
        "treatment": "string",
        "comparator": "string",
        "number_of_patients_enrolled": "string",
        "number_of_patients_randomized": "string",
        "number_of_patients_analyzed": "string",
        "sponsor": "string",
        "study_objective": "string",
        "inclusion_criteria": "string",
        "exclusion_criteria": "string",
        "data_source": "string",
        "study_method": "string",
        "statistical_analysis": "string",
        "study_duration": "string",
        "outcomes_reported": "string",
        "limitations_of_the_study": "string",
        "authors_conclusion": "string",
        "comment": "string"
    },
    "Baseline Characteristics": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "disease_type": "string",
        "treatment_comparator": "string",
        "sample_size_itt": "string",
        "overall_subgroup": "string",
        "male_evaluable_n": "string",
        "male_n": "string",
        "male_percent": "string",
        "male_comments": "string",
        "female_n": "string",
        "female_percent": "string",
        "female_comments": "string",
        "age_evaluable_n": "string",
        "age_mean_sd": "string",
        "age_median_range": "string",
        "disease_severity": "string",
        "disease_severity_n": "string",
        "disease_severity_percent": "string",
        "disease_severity_comments": "string",
        "sunderland_score": "string",
        "diagnostic_evaluation_techniques": "string",
        "race_white": "string",
        "race_black": "string",
        "race_other": "string",
        "body_mass_index": "string",
        "duration_of_symptoms": "string",
        "nerve_type": "string",
        "site_of_injury": "string",
        "cause_of_injury": "string",
        "type_of_procedure": "string",
        "usa_region": "string",
        "comorbidities": "string",
        "charlson_comorbidity_index": "string",
        "insurance_type": "string",
        "functional_deficits": "string",
        "healthcare_providers_involved": "string",
        "other_key_baseline_characteristics": "string"
    },
    "Treatment Pathways": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "surgery_detail": "string",
        "line_of_therapy": "string",
        "concomitant_therapies_surgeries": "string",
        "prior_therapies_surgeries": "string",
        "subsequent_therapies_surgeries": "string",
        "patients_receiving_physical_therapy_etc": "string",
        "comments": "string"
    },
    "Unmet needs": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "unmet_needs": "string",
        "comments": "string"
    },
    "Natural History": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "reoperation_rates": "string",
        "rate_of_recovery": "string",
        "factors_influencing_recovery": "string"
    },
    "Clinical Outcomes (Continuous)": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "evaluable_n": "string",
        "number_of_wrists": "string",
        "outcome": "string",
        "criteria_definition": "string",
        "mean": "string",
        "sd": "string",
        "median": "string",
        "range": "string",
        "iqr": "string",
        "ci_95": "string",
        "p_value": "string",
        "hr_ratio": "string",
        "km_curve": "string",
        "comments": "string"
    },
    "Clinical Outcomes (Dichotomous)": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "evaluable_n": "string",
        "outcome": "string",
        "criteria_definition": "string",
        "n": "string",
        "percent": "string",
        "p_value": "string",
        "km_curve": "string",
        "comments": "string"
    },
    "Humanistics outcomes": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "type_of_outcome": "string",
        "scale_questionnaire": "string",
        "total_score_domains": "string",
        "evaluable_n": "string",
        "n": "string",
        "percent": "string",
        "mean": "string",
        "sd": "string",
        "se": "string",
        "median": "string",
        "range": "string",
        "iqr": "string",
        "p_value": "string",
        "ci_95": "string",
        "hr_ratio": "string",
        "comments": "string"
    },
    "Economic costs": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "sample_size_itt": "string",
        "type_of_study": "string",
        "type_of_cost": "string",
        "cost_year": "string",
        "currency": "string",
        "cost_item": "string",
        "cost_unit_type": "string",
        "timeframe": "string",
        "cost_data_mean": "string",
        "cost_data_median": "string",
        "cost_data_range": "string",
        "cost_data_sd": "string",
        "work_productivity_loss_absenteeism": "string",
        "work_productivity_loss_presenteeism": "string",
        "work_loss_impairment": "string",
        "disability_related_productivity_loss": "string",
        "key_drivers": "string",
        "source": "string",
        "comments": "string"
    },
    "Economic resources": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "sample_size_itt": "string",
        "type_of_study": "string",
        "resource_use_item": "string",
        "units_timeframe": "string",
        "number_of_resources_used": "string",
        "mean": "string",
        "median": "string",
        "work_productivity_loss_absenteeism": "string",
        "work_productivity_loss_presenteeism": "string",
        "key_drivers": "string",
        "source": "string",
        "comments": "string"
    },
    "Safety": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "any_grade_adverse_event": "string",
        "any_serious_adverse_event": "string",
        "any_grade_3_4_adverse_event": "string",
        "complications": "string",
        "specific_aes": "string",
        "list_of_specific_adverse_events": "string"
    },
    "Tolerability": {
        "study_id": "string",
        "author_and_year_of_publication": "string",
        "study_name": "string",
        "treatment_comparator": "string",
        "disease_type": "string",
        "overall_subgroup": "string",
        "time_point": "string",
        "time_point_details": "string",
        "sample_size_itt": "string",
        "withdrawals_discontinuations_all": "string",
        "withdrawals_lack_of_efficacy": "string",
        "withdrawals_due_to_aes": "string",
        "withdrawals_other_reason": "string"
    },
    "Recommendations (Item no)": {
        "q1_hypothesis_aim_objective_described": "string",
        "q2_main_outcomes_described": "string",
        "q3_characteristics_patients_described": "string",
        "q4_interventions_described": "string",
        "q5_confounders_described": "string",
        "q6_main_findings_described": "string",
        "q7_random_variability_estimates": "string",
        "q8_adverse_events_reported": "string",
        "q9_lost_to_followup_described": "string",
        "q10_probability_values_reported": "string",
        "q11_subjects_representative": "string",
        "q12_participating_subjects_representative": "string",
        "q13_staff_facilities_representative": "string",
        "q14_attempt_blind_subjects": "string",
        "q15_attempt_blind_assessors": "string",
        "q16_data_dredging_clear": "string",
        "q17_analyses_adjust_followup": "string",
        "q18_statistical_tests_appropriate": "string",
        "q19_compliance_reliable": "string",
        "q20_outcome_measures_accurate": "string",
        "q21_recruited_same_population": "string",
        "q22_recruited_same_period": "string",
        "q23_randomized_intervention_groups": "string",
        "q24_randomized_assignment_concealed": "string",
        "q25_adequate_adjustment_confounding": "string",
        "q26_losses_followup_accounted": "string",
        "q27_sufficient_power": "string"
    },
    "NICE Checklist": {
        "study_id": "string",
        "randomization_appropriate": "string",
        "randomization_justification": "string",
        "allocation_concealment_adequate": "string",
        "allocation_concealment_justification": "string",
        "groups_similar_at_outset": "string",
        "groups_similar_justification": "string",
        "care_providers_blinded": "string",
        "care_providers_blinded_justification": "string",
        "unexpected_imbalances_in_dropouts": "string",
        "unexpected_imbalances_justification": "string",
        "measured_more_outcomes_than_reported": "string",
        "measured_more_outcomes_justification": "string",
        "intention_to_treat_analysis": "string",
        "intention_to_treat_justification": "string"
    }
}

def map_type(type_str: str) -> Type:
    type_str = type_str.lower()
    if type_str in ["integer", "int"]:
        return int
    elif type_str in ["float", "decimal"]:
        return float
    elif type_str in ["boolean", "bool"]:
        return bool
    elif type_str == "list_of_strings":
        return List[str]
    else:
        return str

def build_dynamic_schema(template_name: str, schema_dict: dict) -> Type[BaseModel]:
    """
    Dynamically builds a Pydantic model for the given schema dictionary.
    Each field is wrapped in an object containing 'value' and 'verbatim_quote'.
    """
    fields = {}
    for param_name, data_type_str in schema_dict.items():
        python_type = map_type(data_type_str)
        
        # Create a nested model for each parameter
        NestedModel = create_model(
            f"{param_name.capitalize()}Extraction",
            value=(Optional[python_type], Field(default=None, description=f"The extracted value for {param_name}. Must match type {data_type_str}.")),
            verbatim_quote=(Optional[str], Field(default=None, description="Exact 5 to 12 words from the source text where this metric was found. DO NOT paraphrase."))
        )
        
        fields[param_name] = (Optional[NestedModel], Field(default=None, description=f"Extraction wrapper for {param_name}"))
    
    # Create the top level model
    return create_model(f"{template_name.replace(' ', '')}Schema", **fields)

def get_template_names():
    return list(PREDEFINED_TEMPLATES.keys())

def get_template_schema(template_name: str) -> dict:
    return PREDEFINED_TEMPLATES.get(template_name, {})
