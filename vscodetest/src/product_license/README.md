This app is used for working with the license that allows customers to use the product.
That license/ product might be for OneFuse or CloudBolt CMP, tho this code was
originally written for the latter and is therefore more closely/ often tied to it.

For both products, the expectation is that a User cannot use them until they apply
a license. When there is not a valid license available, any attempt to access the
product will direct them to a page where they can apply one, which is generic across
both products. After entering a license, they get a confirmation page that shows some
basic details, including which product it is for. After confirmation, an "Apply Personality"
job runs behind-the-scenes to finish configuring the appliance for the appropriate product.
At the time of writing, that basically just means configuring the DB appropriately using
cb_minimal or fuse_minimal. Our apache configuration also includes different directives for
the different products, but nothing is changed during the job to accomplish that.
While the job is running, the User should not be able to do anything and will instead
see a page telling them it's in progress, similar to what we do with maintenance mode for
upgrades. That is accomplished using a check in the LicenseMiddleware for the case where
we have a valid license but the personality has not been set in GlobalPreferences yet
(which the job does at the end to indicate its completion).

The management command apply_license_personality.py just runs the "Apply Personality"
job, allowing it to be calling programmatically by devs and from things like automated
tests.

The cb_license.py file includes a CloudBoltLicense class that is very useful for checking
the state of your product license, such as whether it's valid (is_valid) or whether it's for
Fuse (license_is_for_fuse(), where if not it's assumed to be CB CMP).

The LicenseMiddleware is used to ensure that the product has a valid license, and also
helps lock down the product when the personality is still in the process of being applied.

The initial steps of apply -> confirm -> upload -> apply personality apply to both
products. The CB CMP product also has a page in its UI that allows Admins to see the
details of their current license, which is done using the templates/product_license/detail.html
template (the product_license/templates/product_license/detail.html one appears to not be
used and can probably be removed).
