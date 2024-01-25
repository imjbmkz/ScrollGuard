from pprint import pprint
from sys import argv
from pandas import concat
from fastapi import FastAPI
from scrollguard.utils import get_config
from scrollguard.etl import extract_collection, standardize_name, metaphone_name
from scrollguard.screening import calculate_ratio

SCREENING_THRESH = get_config()["GENERAL"]["SCREENING_THRESH"]

def screen_name(names: str | list) -> dict:
    """ Returns the screening results of the names entered
    """
    # Get all names to screen and their cleaned version
    names_to_screen = names.split(",") if isinstance(names, str) else names
    standardized_names = [standardize_name(name) for name in names_to_screen]
    metaphone_names = [metaphone_name(name) for name in standardized_names]

    # Get consolidated sanctions and placeholder for screening results
    consolidated_sanctions = extract_collection("CONSOLIDATED_SANCTIONS")
    screening_results = []

    for name, std_name, mtp_name in zip(names_to_screen, standardized_names, metaphone_names):
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

# Define API app
app = FastAPI()

@app.get("/")
async def root():
    """ Homepage of the API
    """
    return {
        "app": "ScrollGuard Sanction Screening API",
        "version": 0.1
    }

@app.get("/screen")
async def screen(name: str):
    # Get all names to be screened
    names_to_screen = name.split(",")
    results = screen_name(names_to_screen)
    return results

if __name__=="__main__":

    # Get all names to be screened
    names_to_screen = argv[1:]
    results = screen_name(names_to_screen)

    # Display results on the console
    pprint(results)