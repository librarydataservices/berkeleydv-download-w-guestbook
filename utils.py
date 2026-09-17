import json
import pandas as pd


def format_guestbook_template(guestbook: dict) -> tuple[dict, dict]:
    """
    Format a guestbook template into a form specification and a response template.

    parameters:
        - guestbook: dict
           A guestbook JSON response returned from the Dataverse API.

    returns:
        - tuple[dict, dict]
            A tuple containing the form specification and the response template.
    """
    # Standard fields offered by dataverse guestbooks.
    # These fields are always present in the guestbook response, but may not be required.
    standard_fields = [
        {
            "name": "name",
            "required": guestbook.get("nameRequired", False),
        },
        {
            "name": "email",
            "required": guestbook.get("emailRequired", False),
        },
        {
            "name": "institution",
            "required": guestbook.get("institutionRequired", False),
        },
        {
            "name": "position",
            "required": guestbook.get("positionRequired", False),
        },
    ]

    # Collect any custom questions, valid responses, and if they are required.
    questions = []
    for q in sorted(guestbook.get("customQuestions", []), key=lambda x: x.get("displayOrder", 0)):
        if q.get("hidden"):
            continue

        questions.append({
            "id": q["id"],
            "question": q["question"],
            "required": q.get("required", False),
            "type": q.get("type", "text"),
            "options": [
                {
                    "id": ov["id"],
                    "value": ov["value"]
                }
                for ov in sorted(q.get("optionValues", []), key=lambda x: x.get("displayOrder", 0))
            ]
        })

    # Create the form specification.
    form_spec = {
        "guestbook_id": guestbook["id"],
        "guestbook_name": guestbook["name"],
        "standard_fields": standard_fields,
        "questions": questions,
    }

    # Create a response template with empty values for standard fields and questions.
    response = {}

    for field in form_spec["standard_fields"]:
        response[field["name"]] = ""

    if form_spec["questions"]:
        response["answers"] = []

        for q in form_spec["questions"]:
            response["answers"].append({
                "id": q["id"],
                "value": None,
            })

    return form_spec, response


def guestbook_questions_table(guestbook: dict) -> pd.DataFrame:
    """
    Create a pandas DataFrame containing the questions and allowed responses from a guestbook.

    parameters:
        - guestbook: dict
            A guestbook JSON response returned from the Dataverse API.

    returns:
        - pd.DataFrame
            A DataFrame containing the questions and allowed responses.

    """
    rows = []

    # For each custom questions, add a row to the DataFrame
    # Collect information on id, required, type, allowed responses, and question text.
    for q in sorted(guestbook.get("customQuestions", []), key=lambda x: x.get("displayOrder", 0)):
        if q.get("hidden"):
            continue

        allowed = ""
        if q.get("type") == "options":
            allowed = "; ".join(
                ov["value"]
                for ov in sorted(q.get("optionValues", []), key=lambda x: x.get("displayOrder", 0))
            )

        rows.append({
            "id": q["id"],
            "required": q.get("required", False),
            "type": q.get("type", "text"),
            "allowed responses": allowed,
            "question": q["question"],
        })

    return pd.DataFrame(rows)


def validate_response(form_spec: dict, user_response: dict):
    """
    Validate a user JSON response against the form specification.

    parameters:
        - form_spec: dict
            A form specification returned from the format_guestbook_template function.
        - user_response: dict
            A completed JSON guestbook response to validate against the form specification.
    """
    errors = []

    # Check that each required standard field is present and not empty.
    for field in form_spec["standard_fields"]:
        if field["required"]:
            value = user_response.get(field["name"])
            if not value or not str(value).strip():
                errors.append(f"Missing required field: {field['name']}")

    answers = user_response.get("answers", [])

    # Check that answers to custom questions are formatted as a list
    if form_spec["questions"]:
        if not isinstance(answers, list):
            errors.append("'answers' must be a list.")
            return errors

    #Check that items in the answers list are a dictionary with an 'id' and a 'value' key
    submitted_answers = {}
    for i, answer in enumerate(answers):
        if not isinstance(answer, dict):
            errors.append(f"answers[{i}] must be a dict.")
            continue

        if "id" not in answer:
            errors.append(f"answers[{i}] is missing 'id'.")
            continue

        if "value" not in answer:
            errors.append(f"answers[{i}] is missing 'value'.")
            continue

        submitted_answers[answer["id"]] = answer["value"]

    # Check that each required custom question has an answer and that the answer is valid.
    for q in form_spec["questions"]:
        answer = submitted_answers.get(q["id"])

        if q["required"] and (answer is None or answer == "" or answer == []):
            errors.append(f"Missing required answer for question {q['id']}")

        if answer is not None and q["type"] == "options":
            allowed = {opt["value"] for opt in q["options"]}
            if answer not in allowed:
                errors.append(
                    f"Invalid answer for question {q['id']}. "
                    f"Expected one of: {sorted(allowed)}; got: {answer!r}"
                )

    # If there are any errors, print them. Otherwise, indicate that the response is valid.
    if errors:
        print(errors)
    else:
        print("No errors found. Proceed to submit the guestbook response.")


def extract_signed_url(response_json: dict) -> str:
    """
    Extract the signed URL from a Dataverse API response JSON.

    parameters:
        - response_json: dict
            A JSON response returned from the Dataverse API containing a signed URL.
    
    returns:
        - str
            The signed URL extracted from the response JSON.
    """
    # Check if the response_json contains the expected keys and extract the signed URL.
    try:
        return response_json["data"]["signedUrl"]
    except KeyError as e:
        raise ValueError(
            "Expected signed URL at response_json['data']['signedUrl'], "
            f"but it was missing. Response was: {response_json}"
        ) from e