from consumer.rest_client import ApiClient
from credentials import API_CREDENTIALS, API_DOMAIN
import requests
import os

import json

# This is the code that actually does the processing of a webhook.
# It is designed to be run asynchronously using a queue consumer.
# To run this, first run an instance of redis using:
# docker-compose up -d.
# Then run:
# rq worker


API_CLIENT = ApiClient(bearer_token_args=API_CREDENTIALS)

# Gets evidence metadata from Axon's evidence API
def get_evidence(agency_id: str, evidence_id: str):
    url = f"https://{API_DOMAIN}/api/v1/agencies/{agency_id}/evidence/{evidence_id}"
    result = API_CLIENT.get(url)
    if result.status_code != 200:
        raise Exception(f"Got status code {result.status_code}:\n{result.content}")
    return result.json()


def get_evidence_file(link: str, file_name: str, case_id: str):
    url = f"https://{API_DOMAIN}{link}"
    file_stream = API_CLIENT.get(url, stream=True)
    if file_stream.status_code != 200:
        raise Exception(
            f"Got status code {file_stream.status_code}:\n{file_stream.content}"
        )
    print(f"Downloading file {file_name}")

    case_evidence_dir = f"evidence/{case_id}"
    if not os.path.exists(case_evidence_dir):
        os.mkdir(case_evidence_dir)

    with open(f"{case_evidence_dir}/{file_name}", "wb") as f:
        for block in file_stream.iter_content(chunk_size=1024 * 1024):
            f.write(block)


# Processes an incoming webhook payload. Consumes the entire payload,
# gets evidence from case and "syncs" it with our local metadata copy.
def process_webhook(payload: dict):
    action = payload["action"]
    if action != "CASE_UPDATED":
        print("This is not a case update, nothing to do")
        return
    case_id = payload["context"]["id"]
    agency_id = payload["agencyId"]
    evidence_ids = payload["context"]["attributes"]["evidenceIds"]
    print(f"Got case ID {case_id}, agency ID {agency_id}")
    print(f"Storing evidence IDs {evidence_ids}")

    with open("evidence.json", "r") as f:
        stored_evidence = json.loads(f.read())

    to_add = set(evidence_ids) - set(stored_evidence.get(case_id, {}).keys())
    to_delete = set(stored_evidence.get(case_id, {}).keys()) - set(evidence_ids)

    print(f"Adding evidence IDs {to_add}")

    for id in to_add:
        print(f"Getting evidence ID {id}")
        evidence = get_evidence(agency_id=agency_id, evidence_id=id)
        if case_id not in stored_evidence:
            stored_evidence[case_id] = {}
        stored_evidence[case_id][id] = evidence

        evidence_file_links = evidence["data"]["relationships"]["files"]["data"]
        for file in evidence_file_links:
            evidence_file_name = file["attributes"]["fileName"]
            evidence_link = file["links"]["related"]
            print(f"Downloading {evidence_link} -> {evidence_file_name}")
            get_evidence_file(
                link=evidence_link, file_name=evidence_file_name, case_id=case_id
            )

    print(f"Deleting evidence IDs {to_delete}")
    for id in to_delete:
        if id in stored_evidence:
            del stored_evidence[case_id][id]

    with open("evidence.json", "w+") as f:
        f.write(json.dumps(stored_evidence, indent=2))
