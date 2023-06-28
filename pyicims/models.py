"""Models."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class People(BaseModel):
    """People: mimics the response from the search/people endpoint."""

    self: str
    id: str


class Person(BaseModel):
    """Person: used to map the response from the profile endpoint."""

    id: int
    folder_id: str
    status: str
    first_name: str
    last_name: str


class Offer(BaseModel):
    """Offer: mimics the response from the offer/search endpoint."""

    TOffer_FCreatedDate_DateOffset: int
    TOffer_TSubmittal_FTitlePerson_LinkUrl: str
    TOffer_FPermission: str
    TOffer_TSubmittal_FTitleJob: str
    TOffer_TSubmittal_FTitlePerson: str
    TOffer_FCreatedDate: datetime
    TOffer_FSubmittalID: int
    TOffer_FArchived: bool
    TOffer_FDeliveryType: Optional[str]
    TOffer_FSentDate: Optional[datetime]
    TOffer_FUpdatedDate_DateOffset: int
    TOffer_TOfferStatus_FCreatedDate_DateOffset: int
    TOffer_TOfferStatus_FStatus: str
    TOffer_FSentDate_DateOffset: Optional[int]
    TOffer_FDeliveryTypeValue: Optional[int]
    TOffer_FOfferID: str
    TOffer_FRecent: str
    TOffer_FJobPersonTitle: str
    TOffer_FUpdatedDate: datetime
    TOffer_TOfferStatus_FCreatedDate: datetime
    TOffer_TSubmittal_FTitleJob_LinkUrl: str
    TOffer_TOfferStatus_FStatusValue: int
    TOffer_TSubmittal_TPerson_FPersonID: str
