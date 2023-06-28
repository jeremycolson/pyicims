"""Offers."""
import os
import requests
import time

from pathlib import Path
from requests import Response
from typing import Any

from pyicims.models import Offer
from pyicims.settings import iCIMSUrls
from pyicims.utilities import generate_auth_token_header, get_offer_path

urls: iCIMSUrls = iCIMSUrls()


def get_offers() -> list[Offer]:
    """Retrieves a list of offers.

    Args:
        None.

    Raises:
        Exception: When there are less offers than expected (likely pageSize issue).
        Exception: When there is a record mismatch.

    Returns:
        list[Offer]: List of offer objects from iCIMS.
    """
    offers: list[Offer] = []

    params: dict[str, Any] = {
        "page": 0,
        "pageSize": 3000,
        "sort": {"field": "TOffer_FOfferID", "direction": "asc"},
    }

    headers: dict[str, str] = generate_auth_token_header()
    res: Response = requests.post(urls.search_offer_url, headers=headers, json=params)
    res_offers: dict[str, Any] = res.json()

    if res_offers["results"]:
        for this_offer in res_offers["results"]["results"]:
            offers.append(Offer.parse_obj(this_offer))

        total_offers: int = res_offers["results"]["total"]
        offer_count: int = len(offers)
        message: str = ""

        if total_offers > offer_count:
            message = f"Offer Mismatch: expected {total_offers}, found {offer_count}). "
            message += "Consider increasing the pageSize (see post params)."
            raise Exception(message)
        elif total_offers != offer_count:
            message = f"Offer Mismatch: expected {total_offers}, found {offer_count})."
            raise Exception(message)

    return offers


def regenerate_offer_letter(offer_id: str, signed: bool = True) -> None:
    """Regenerate the offer letter (pdf) for a specific offer id.

    Args:
        offer_id (int): offer id
        signed (bool): generate signed offer letter
    """
    headers: dict[str, str] = generate_auth_token_header()
    url: str = iCIMSUrls.offer_document_url
    params: dict[str, Any] = {"offerId": offer_id, "signed": signed, "force": True}

    # don't ask... iCIMS APIs = dumb
    json: dict[str, str] = {"ping": "pong"}

    res: Response = requests.post(url, headers=headers, params=params, json=json)
    res.raise_for_status()


def get_offer_letter(
    offer_id: str, person_id: str, signed: bool = True, regen: bool = False
) -> None:
    """Get the offer letter (pdf) for a specific offer id.

    Args:
        offer_id (str): offer id (for the offer letter to retrieve).
        person_id (str): person id (used to name the offer letter file).
        signed (bool, optional): whether the PDF should be signed.
        regen (bool, optional): if the offer letter is not available, regenerate if True.

    Raises:
        Exception: if the file type of the resume is of unknown format.
    """
    headers: dict[str, str] = generate_auth_token_header()
    url: str = iCIMSUrls.offer_document_url
    params: dict[str, Any] = {"offerId": offer_id, "signed": signed}

    try:
        res: Response = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"could not retrieve offer letter (offer_id: {offer_id}): {error}")

        if regen:
            print(f"regenerating offer letter (offer_id: {offer_id})")
            regenerate_offer_letter(offer_id=offer_id, signed=signed)
            get_offer_letter(offer_id=offer_id, person_id=person_id)
    else:
        file_name: str = f"{person_id}_offer_letter.pdf"
        path: Path = get_offer_path(file_name)

        with open(path, "wb") as out_file:
            out_file.write(res.content)


def get_all_offer_letters(regen: bool = False) -> None:
    """Retrieve all offer letters.

    Args:
        regen (bool, optional): if the offer letter is not available, regenerate if True.
    """
    path: Path = Path(__file__).parent.parent / "docs" / "offer_letters"

    # create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    files: list[str] = os.listdir(path=path)
    files = [file.split(".")[0] for file in files]
    file_names: set[str] = set(files)
    offers: list[Offer] = get_offers()
    total: int = len(offers)
    counter: int = 1

    for offer in offers:
        if offer.TOffer_TOfferStatus_FStatus == "Offer accepted":
            print(
                f"processing offer letter {counter}/{total} for offer id: {offer.TOffer_FOfferID}"
            )
            offer_id: str = offer.TOffer_FOfferID
            person_id: str = offer.TOffer_TSubmittal_TPerson_FPersonID
            file_name: str = f"{person_id}_offer_letter"

            if file_name not in file_names:
                get_offer_letter(offer_id=offer_id, person_id=person_id)
                time.sleep(0.1)

        counter += 1
