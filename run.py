"""Downloads all the resumes and offer letters."""
from pyicims.people import get_all_resumes
from pyicims.offers import get_all_offer_letters


if __name__ == "__main__":
    get_all_resumes()
    get_all_offer_letters()
