import json
import pandas as pd


def format_guestbook_template(guestbook: dict) -> tuple[dict, dict]:
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

    form_spec = {
        "guestbook_id": guestbook["id"],
        "guestbook_name": guestbook["name"],
        "standard_fields": standard_fields,
        "questions": questions,
    }

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
    rows = []

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
    errors = []

    for field in form_spec["standard_fields"]:
        if field["required"]:
            value = user_response.get(field["name"])
            if not value or not str(value).strip():
                errors.append(f"Missing required field: {field['name']}")

    answers = user_response.get("answers", [])

    if form_spec["questions"]:
        if not isinstance(answers, list):
            errors.append("'answers' must be a list.")
            return errors

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

    if errors:
        print(errors)
    else:
        print("No errors found. Proceed to submit the guestbook response.")


def extract_signed_url(response_json: dict) -> str:
    candidates = [
        response_json.get("data", {}).get("url"),
        response_json.get("data", {}).get("signedUrl"),
        response_json.get("url"),
        response_json.get("signedUrl"),
    ]

    for candidate in candidates:
        if candidate:
            return candidate

    raise ValueError(
        "Could not find signed URL in response JSON. "
        "Inspect signed_url_json to determine the correct field."
    )