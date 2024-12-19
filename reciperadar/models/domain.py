from reciperadar import db
from reciperadar.models.base import Storable


class Domain(Storable):
    """
    This data model represents a single top-level DNS domain name;
    'example.com' would appear as a single item within the corresponding
    database table.

    Domains are automatically created the first time a recipe is indexed
    from a never-previously-seen top-level domain name.

    The purpose of the model is to keep a record of whether consent has
    been provided by the owner(s) of each domain name to display thumbnail
    images and a website icon when recipes from that domain are displayed in
    search results.

    Given that purpose -- indication of consent -- we also store a free-text
    contact information field here, that in many cases contains an email
    address, but in some cases may contain, for example, a website URL for
    a contact form.  We have a legitimate interest in storing this
    potentially-personal data because we use that information to make contact
    with the website owner(s) to request consent, something that is not
    assumed to be given by default.
    """

    __tablename__ = "domains"

    domain = db.Column(db.String, primary_key=True)
    crawl_enabled = db.Column(db.Boolean)
    cache_enabled = db.Column(db.Boolean)
    contact = db.Column(db.String)
    approval = db.Column(db.String)
    approved_at = db.Column(db.TIMESTAMP(timezone=True))
