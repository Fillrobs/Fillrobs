# Authentication

Supports CloudBolt's Identity and Authentication services.

_Note: Currently, this app only handles Single Sign-On (SSO)_.

_To-Do: Move LDAP logic out of `utilities` and into this module._

## Architecture

### Single Sign-On (SSO)

#### Background

_Quick overview: In SSO, a "Service Provider" (SP, e.g. CloudBolt) connects to
an "Identity Provider" (IdP, e.g. Okta, OneLogin) service, which is responsible
for managing users. "SAML" is the protocol upon which SSO is built._

Currently, the operative SSO SP views / URLs are **Login**, **Metadata**, and
**ACS**:

* The "Login" URL is used when a user wants to access the SP, which then causes
  the SP to reach out to the IdP for user authentication.
* The "Metadata" URL is used for generating the SP's XML-formatted information
  that is sent to the IdP required for initiating the SAML handshake.
* The "ACS" URL is where an IdP `POST`'s to when an IdP-authenticated user wants
  to access the SP, and the data received by the SP is used to authenticate the
  user on the SP side.

#### Components

This feature depends heavily on the `pysaml2` library. Some implementation
decisions were made to both ensure compatibility with the OOTB behaviors of this
package and enforce best-practices for this project (e.g. using temporary
directories to write files that are otherwise stored in the database.)

* **Models**: All SSO IdP models are `proxy` models off of the
  `BaseSSOProvider`, meaning that they use a single database table to support
   the different IdPs.
* **Services**: The `SSOInterface` provides a single interface for handling
  business logic for the different SSO models.
* **Backends**: The `Saml2Backend` is responsible for handling user
  authentication when a SAML response is `POST`'ed to the ACS endpoint.
* **Caches**: The various cache objects in `authentication/cache.py` support the
  `Saml2Backend`.
* **Everything Else**: Views, Forms, URLs, etc. are mostly standard fare. There
  are specific components in support of the Login, Metadata, and ACS pathways
  described above, but the majority of the logic for those components are
  handled in the aforementioned Models, Services, and Backends.
