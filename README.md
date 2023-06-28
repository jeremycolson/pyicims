# pyiCIMS

This basic module is used to retrieve all resumes and offer letters from iCIMS.

> **Warning**: There is an API limit of 10,000 hits per today. If you plan on exceeding this limit, please contact the iCIMS Account Manager to have this limit increased.

For more information on the relevant iCIMS API Endpoints, see:
- [Search](https://developer.icims.com/REST-API/Object-Types-Commands/Search-API)
- [Offer](https://developer.icims.com/REST-API/Object-Types-Commands/Offer-API)
- [Binary Files](https://developer.icims.com/REST-API/Object-Types-Commands/Binary-Files)
- [Profiles](https://developer.icims.com/REST-API/Object-Types-Commands/Profiles)

For more information on the relevant iCIMS Data Models, see:
- [Person](https://developer.icims.com/Data-Models/Person-Profile/Person)

> **Note**: You will need to register to access the iCIMS developer portal. Once registered, please reach out to the iCIMS Account Manager to expedite access.

<br>

## Need to Know

You'll need to have a basic graps on the basics of:
- [Python](https://docs.python.org/3/)
- [Poetry](https://python-poetry.org/)
- [iCIMS](https://developer.icims.com)

<br>

## Installs

The following tools should be installed:
- [Python](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Visual Studio Code](https://code.visualstudio.com/download)

<br>

## Setup

1. You will need to obtain the iCIMS client id and client secret (see key vault)
2. You will need to obtain the iCIMS customer id (see key vault)
3. Update the test.env file with the customer id and client id
4. Rename the test.env file to .env
5. Run `echo <client secret> secrets/client_secret` (where `<client_secret>` is the actual client secret)
6. Run `cat secrets/client_secret` to confirm the secret was saved properly
7. Run `poetry config virtualenvs.in-project true`
8. Run `poetry install`


<br>

## iCIMS Auhtorization Flow (OAuth 2)

![Authorization Flow](/media/app_auth_workflow.png)