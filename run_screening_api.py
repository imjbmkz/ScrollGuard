from pandas import concat
from fastapi import FastAPI
from scrollguard.utils import get_config
from scrollguard.etl import extract_collection, standardize_name, metaphone_name
from scrollguard.screening import calculate_ratio

SCREENING_THRESH = get_config()["GENERAL"]["SCREENING_THRESH"]

# Get consolidated sanctions
consolidated_sanctions = extract_collection("CONSOLIDATED_SANCTIONS")

app = FastAPI()

@app.get("/")
async def root():
    return {
        "app": "ScrollGuard Sanction Screening API",
        "version": 0.1
    }

@app.get("/screen")
async def screen(name: str):
    names = name.split(",")
    screening_results = []

    # Get the cleaned version of the names
    std_names = [standardize_name(n) for n in names]
    mtp_names = [metaphone_name(s) for s in std_names]

    for name, std_name, mtp_name in zip(names, std_names, mtp_names):
        # Get a copy of the sanctions list with extra columns
        screening_result = consolidated_sanctions.copy()
        screening_result["NAME_TO_SCREEN"] = name
        screening_result["STD_NAME_TO_SCREEN"] = std_name
        screening_result["MTP_NAME_TO_SCREEN"] = mtp_name

        # Get Levenshtein ratio on standardized name and name metaphone
        screening_result["LEV_RATIO_STD_NAME"] = screening_result["STANDARDIZED_NAME"].apply(
            calculate_ratio, **{"s2": std_name, "is_sorted": True}
        )
        screening_result["LEV_RATIO_MTP_NAME"] = screening_result["METAPHONE_NAME"].apply(
            calculate_ratio, **{"s2": mtp_name, "is_sorted": True}
        )

        # Filter results based on threshold
        results_criteria = ((screening_result["LEV_RATIO_STD_NAME"]>=SCREENING_THRESH) | 
                            (screening_result["LEV_RATIO_MTP_NAME"]>=SCREENING_THRESH))
        screening_results.append(screening_result[results_criteria])

    # Consolidate and display the results
    screening_results_dict = concat(screening_results, ignore_index=True).to_dict(orient="records")
    
    return screening_results_dict