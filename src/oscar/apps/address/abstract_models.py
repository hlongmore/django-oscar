import re

from dj_address.models import AddressField
from django.conf import settings
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from phonenumber_field.modelfields import PhoneNumberField

from oscar.core.compat import AUTH_USER_MODEL
from .utils import POSTCODES_REGEX, TITLE_CHOICES


class AbstractAddress(models.Model):
    """
    Superclass address object

    This is subclassed and extended to provide models for
    user, shipping and billing addresses.
    """
    postcode_required = 'postcode' in settings.OSCAR_REQUIRED_ADDRESS_FIELDS
    title = models.CharField(
        pgettext_lazy(u"Treatment Pronouns for the customer", u"Title"),
        max_length=64, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(_("First name"), max_length=255, blank=True)
    last_name = models.CharField(_("Last name"), max_length=255, blank=True)
    address = AddressField(on_delete=models.PROTECT)

    def __str__(self):
        return self.summary

    class Meta:
        abstract = True
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def clean(self):
        # Strip all whitespace for fields not managed by dj_address or choices.
        for field in ['first_name', 'last_name']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

        # Ensure postcodes are valid for country
        self.ensure_postcode_is_valid_for_country()

    def ensure_postcode_is_valid_for_country(self):
        """
        Validate postcode given the country
        """
        address = self.address
        postcode = address.locality.postal_code
        country_code = address.locality.state.country.code
        regex = POSTCODES_REGEX.get(country_code, None)
        if self.postcode_required and country_code and not postcode:
            if regex:
                msg = _(f"Addresses in {address.country} require a valid postcode")
                raise exceptions.ValidationError(msg)
        if postcode and country_code:
            # Ensure postcodes are always uppercase
            postcode = postcode.upper().replace(' ', '')
            # Validate postcode against regex for the country if available
            if regex and not re.match(regex, postcode):
                msg = _(f'The postcode "{address.locality.postal_code}" is not valid for '
                        f'{address.locality.state.country}')
                raise exceptions.ValidationError({'postcode': [msg]})

    @property
    def city(self):
        """ Some people prefer to call it a city. """
        if self.address.locality:
            return self.address.locality.name
        return ''

    @property
    def summary(self):
        """ Returns a comma-separated string of the address. """
        return u", ".join(self.active_address_fields())

    @property
    def salutation(self):
        """ Name and title. """
        return ' '.join(s for s in [self.get_title_display(), self.first_name, self.last_name] if s)

    @property
    def name(self):
        return ' '.join(s for s in [self.first_name, self.last_name] if s)

    def active_address_fields(self):
        """It appears the goal of this method is to format an address as a typical shipping
        address, so I'm breaking the way it used to work in favor of what it should do.
        """
        receipt_line = self.salutation
        address = self.address
        secondary_line = f' #{address.subpremise}' if address.subpremise else ''
        locality = address.locality
        if locality:
            delivery_line = f'{address.street_number} {address.route}'
            if not delivery_line:
                delivery_line = address.formatted.split(',')[0]
            if delivery_line:
                delivery_line += secondary_line
            state = locality.state
            locality_line = f'{locality.name} {state.code} {locality.postal_code}'
            country_line = state.country.printable_name if state.country.code != 'US' else ''
        else:
            secondary_line = ''
            delivery_line = ''
            locality_line = ''
            country_line = address.raw
        lines = [receipt_line, delivery_line, locality_line, country_line]
        return [line.upper() for line in lines if line]

    def populate_alternative_model(self, address_model):
        """
        For populating an address model using the matching fields
        from this one.

        This is used to convert a user address to a shipping address
        as part of the checkout process.
        """
        destination_field_names = [
            field.name for field in address_model._meta.fields]
        for field_name in [field.name for field in self._meta.fields]:
            if field_name in destination_field_names and field_name != 'id':
                setattr(address_model, field_name, getattr(self, field_name))


class AbstractCountry(models.Model):
    """
    International Organization for Standardization (ISO) 3166-1 Country list.

    The field names are a bit awkward, but kept for backwards compatibility.
    pycountry's syntax of alpha2, alpha3, name and official_name seems sane.
    """
    iso_3166_1_a2 = models.CharField(
        _('ISO 3166-1 alpha-2'), max_length=2, primary_key=True)
    iso_3166_1_a3 = models.CharField(
        _('ISO 3166-1 alpha-3'), max_length=3, blank=True)
    iso_3166_1_numeric = models.CharField(
        _('ISO 3166-1 numeric'), blank=True, max_length=3)

    #: The commonly used name; e.g. 'United Kingdom'
    printable_name = models.CharField(_('Country name'), max_length=128)
    #: The full official name of a country
    #: e.g. 'United Kingdom of Great Britain and Northern Ireland'
    name = models.CharField(_('Official name'), max_length=128)

    display_order = models.PositiveSmallIntegerField(
        _("Display order"), default=0, db_index=True,
        help_text=_('Higher the number, higher the country in the list.'))

    is_shipping_country = models.BooleanField(
        _("Is shipping country"), default=False, db_index=True)

    class Meta:
        abstract = True
        app_label = 'address'
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ('-display_order', 'printable_name',)

    def __str__(self):
        return self.printable_name or self.name

    @property
    def code(self):
        """
        Shorthand for the ISO 3166 Alpha-2 code
        """
        return self.iso_3166_1_a2

    @property
    def numeric_code(self):
        """
        Shorthand for the ISO 3166 numeric code.

        iso_3166_1_numeric used to wrongly be a integer field, but has to be
        padded with leading zeroes. It's since been converted to a char field,
        but the database might still contain non-padded strings. That's why
        the padding is kept.
        """
        return u"%.03d" % int(self.iso_3166_1_numeric)


class AbstractShippingAddress(AbstractAddress):
    """
    A shipping address.

    A shipping address should not be edited once the order has been placed -
    it should be read-only after that.

    NOTE:
    ShippingAddress is a model of the order app. But moving it there is tricky
    due to circular import issues that are amplified by get_model/get_class
    calls pre-Django 1.7 to register receivers. So...
    TODO: Once Django 1.6 support is dropped, move AbstractBillingAddress and
    AbstractShippingAddress to the order app, and move
    PartnerAddress to the partner app.
    """

    phone_number = PhoneNumberField(
        _("Phone number"), blank=True,
        help_text=_("In case we need to call you about your order"))
    notes = models.TextField(
        blank=True, verbose_name=_('Instructions'),
        help_text=_("Tell us anything we should know when delivering "
                    "your order."))

    class Meta:
        abstract = True
        # ShippingAddress is registered in order/models.py
        app_label = 'order'
        verbose_name = _("Shipping address")
        verbose_name_plural = _("Shipping addresses")

    @property
    def order(self):
        """
        Return the order linked to this shipping address
        """
        try:
            return self.order_set.all()[0]
        except IndexError:
            return None


class AbstractUserAddress(AbstractShippingAddress):
    """
    A user's address.  A user can have many of these and together they form an
    'address book' of sorts for the user.

    We use a separate model for shipping and billing (even though there will be
    some data duplication) because we don't want shipping/billing addresses
    changed or deleted once an order has been placed.  By having a separate
    model, we allow users the ability to add/edit/delete from their address
    book without affecting orders already placed.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_("User"))

    #: Whether this address is the default for shipping
    is_default_for_shipping = models.BooleanField(
        _("Default shipping address?"), default=False)

    #: Whether this address should be the default for billing.
    is_default_for_billing = models.BooleanField(
        _("Default billing address?"), default=False)

    #: Track how often an address is used for shipping / billing so we can show
    #: the most popular ones first.
    num_orders_as_shipping_address = models.PositiveIntegerField(
        _("Number of Orders as Shipping Address"), default=0)
    num_orders_as_billing_address = models.PositiveIntegerField(
        _("Number of Orders as Billing Address"), default=0)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Ensure user has only one default each of shipping and billing address. """
        self._ensure_defaults_integrity()
        super().save(*args, **kwargs)

    def _ensure_defaults_integrity(self):
        if self.is_default_for_shipping:
            self.__class__._default_manager.filter(
                user=self.user, is_default_for_shipping=True).update(
                is_default_for_shipping=False)
        if self.is_default_for_billing:
            self.__class__._default_manager.filter(
                user=self.user, is_default_for_billing=True).update(
                is_default_for_billing=False)
    # We let dj_address handle address uniqueness

    class Meta:
        abstract = True
        app_label = 'address'
        verbose_name = _("User address")
        verbose_name_plural = _("User addresses")
        ordering = ['-num_orders_as_shipping_address']


class AbstractBillingAddress(AbstractAddress):
    class Meta:
        abstract = True
        # BillingAddress is registered in order/models.py
        app_label = 'order'
        verbose_name = _("Billing address")
        verbose_name_plural = _("Billing addresses")

    @property
    def order(self):
        """
        Return the order linked to this shipping address
        """
        try:
            return self.order_set.all()[0]
        except IndexError:
            return None


class AbstractPartnerAddress(AbstractAddress):
    """
    A partner can have one or more addresses. This can be useful e.g. when
    determining US tax which depends on the origin of the shipment.
    """
    partner = models.ForeignKey(
        'partner.Partner',
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('Partner'))

    class Meta:
        abstract = True
        app_label = 'partner'
        verbose_name = _("Partner address")
        verbose_name_plural = _("Partner addresses")
