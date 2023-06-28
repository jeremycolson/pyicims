"""People."""
import os
import requests
import time

from pathlib import Path
from requests import Response
from typing import Any

from pyicims.models import People, Person
from pyicims.settings import iCIMSUrls
from pyicims.utilities import generate_auth_token_header, get_resume_path

urls: iCIMSUrls = iCIMSUrls()


def generate_filters(person_id: str = "") -> dict[str, Any]:
    """Generates the employee and profile paging filter (where applicable).

    Args:
        person_id (str, optional): the person id (where the last page ended).

    Returns:
        dict: parameter to be included in next post call (to get next page).

    Notes:
        - Emp:New Hire (C16818)
        - Emp:Current Employee (D32013)
        - Emp:Contractor/Temp (D32017)
        - Emp:Former Employee (D32018)
        - HM:Active (D32011)
        - HM:Inactive (D32012)
        - HM:Active Agency (C14598)
    """
    if person_id:
        params = {
            "filters": [{"name": "person.id", "value": [person_id], "operator": ">"}],
            "operator": "&",
            "children": [
                {
                    "filters": [
                        {"name": "person.folder", "value": ["C16818"]},
                        {"name": "person.folder", "value": ["D32013"]},
                        {"name": "person.folder", "value": ["D32017"]},
                        {"name": "person.folder", "value": ["D32018"]},
                        {"name": "person.folder", "value": ["D32011"]},
                        {"name": "person.folder", "value": ["D32012"]},
                    ],
                    "operator": "|",
                }
            ],
        }
    else:
        params = {
            "filters": [
                {"name": "person.folder", "value": ["C16818"]},
                {"name": "person.folder", "value": ["D32013"]},
                {"name": "person.folder", "value": ["D32017"]},
                {"name": "person.folder", "value": ["D32018"]},
                {"name": "person.folder", "value": ["D32011"]},
                {"name": "person.folder", "value": ["D32012"]},
            ],
            "operator": "|",
        }

    return params


def get_people(person_id: str = "") -> list[People]:
    """Retrieve profiles from iCIMS.

    Args:
        person_id (str, optional): the person id (where the last page ended).

    Notes:
        The filter is only pulling people where a start date has been specified.
        In other words, that should align to employees, and exclude the thousands
        of other people that are in the system (e.g., applicants)

    Returns:
        List[People]: list of people objects from iCIMS.
    """
    people: list[People] = []
    headers: dict[str, str] = generate_auth_token_header()
    params: dict[str, Any] = generate_filters(person_id)
    res: Response = requests.post(urls.search_people_url, headers=headers, json=params)
    res.raise_for_status()
    res_people: dict[str, Any] = res.json()

    if res_people and res_people["searchResults"]:
        for this_person in res_people["searchResults"]:
            people.append(People.parse_obj(this_person))

    return people


def get_all_people() -> list[People]:
    """Retrieve a list of all people in iCIMS.

    Returns:
        list[People]: a list of People objects
            - People.self: url to the specific profile
            - People.id: iCIMS id for the specific profile
    """
    people: list[People] = []
    people_page: list[People] = []

    # get first page of people
    people_page = get_people()
    people = people_page

    while len(people_page) == 1000:
        # we have potentially hit the max for the page or just unluckily hit exactly
        # 1000 people records in the reponse... unfortunately, the API is pretty
        # dumb so we have no way of knowing other than making another call
        last_person: People = people_page[-1]
        people_page = get_people(person_id=last_person.id)

        if len(people_page) > 0:
            # if we find more records on the next page, add them to the people list
            people.extend(people_page)

    return people


def parse_person_id_from_url(url: str) -> int:
    """Parse the person id from the profile url.

    Args:
        url (str): profile url.

    Raises:
        ValueError: if the url is not in the format expected.

    Returns:
        int: the parsed person id
    """
    if not url.startswith(urls.people_url):
        raise ValueError(f"Invlid people URL, expected: {urls.people_url}")
    return int(url.replace(f"{urls.people_url}/", ""))


def get_person(url: str) -> Person:
    """Retrieve person object.

    Args:
        url (str): profile url for the person.

    Returns:
        Person: person object.
    """
    headers: dict[str, str] = generate_auth_token_header()
    res: Response = requests.get(url, headers=headers)
    res_json: dict[str, Any] = res.json()

    person: Person = Person(
        id=parse_person_id_from_url(url),
        folder_id=res_json["folder"]["id"],
        status=res_json["folder"]["value"],
        first_name=res_json["firstname"],
        last_name=res_json["lastname"],
    )

    return person


def get_resume(person_id: str) -> None:
    """Get the resume for a specific person.

    Args:
        person_id (str): person id (for which to retrieve the resume).

    Raises:
        Exception: if the file type of the resume is of unknown format.
    """
    headers: dict[str, str] = generate_auth_token_header()
    url: str = iCIMSUrls.get_resume_url.replace(iCIMSUrls.person_id_placeholder, person_id)
    res: Response = requests.get(url, headers=headers)

    file_type: str = res.headers["Content-Type"]
    file_name: str = f"{person_id}_resume"

    if file_type == "application/pdf":
        file_name += ".pdf"
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_name += ".docx"
    elif file_type == "application/msword":
        file_name += ".doc"
    elif file_type == "image/png":
        file_name += ".png"
    elif file_type == "image/jpeg":
        file_name += ".jpg"
    elif file_type == "text/rtf":
        file_name += ".rtf"
    elif file_type == "text/plain":
        file_name += ".txt"
    elif file_type == "application/json":
        # no resume exists in this case
        write_empty_resume_file(f"{file_name}.none")
        return
    elif file_type == "application/octet-stream":
        # unsupported format
        write_empty_resume_file(f"{file_name}.bad")
        return
    else:
        raise Exception(f"Unknown Content Type: {file_type}")

    path: Path = get_resume_path(file_name)

    with open(path, "wb") as out_file:
        out_file.write(res.content)


def get_all_resumes() -> None:
    path: Path = Path(__file__).parent.parent / "docs" / "resumes"

    # create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    files: list[str] = os.listdir(path=path)
    files = [file.split(".")[0] for file in files]
    file_names: set[str] = set(files)
    people: list[People] = get_all_people()
    total: int = len(people)
    counter: int = 1

    for person in people:
        file_name: str = f"{person.id}_resume"
        print(f"processing resume {counter}/{total} for icims id: {person.id}")

        if file_name not in file_names:
            get_resume(person_id=person.id)
            time.sleep(0.1)

        counter += 1


def write_empty_resume_file(file_name: str) -> None:
    path: Path = get_resume_path(file_name)

    with open(path, "wb"):
        pass
