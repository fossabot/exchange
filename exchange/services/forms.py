# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo, (C) 2018 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from geonode.services.forms import CreateServiceForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.conf import settings
try:
    if 'ssl_pki' not in settings.INSTALLED_APPS:
        raise ImportError
    from ssl_pki.models import (
        has_ssl_config,
        ssl_config_for_url
    )
except ImportError:
    has_ssl_config = None
    ssl_config_for_url = None


class ExchangeCreateServiceForm(CreateServiceForm):
    @staticmethod
    def validate_pki_url(url):
        """Validates the pki protected url and its associated certificates"""
        ssl_config = ssl_config_for_url(url)
        try:
            if ssl_config is None:
                # Should have an SslConfig, but this could happen
                raise ValidationError
            ssl_config.clean()
        except ValidationError:
            raise ValidationError(
                _("Error with SSL or PKI configuration for url: %(url)s. "
                  "Please contact your Exchange Administrator."),
                params={
                    "url": url,
                }
            )

    def clean(self):
        """Validates form fields that depend on each other"""
        url = self.cleaned_data.get("url")
        service_type = self.cleaned_data.get("type")
        if url is not None and service_type is not None:
            # Check pki validation
            if callable(has_ssl_config) and has_ssl_config(url):
                self.validate_pki_url(url)

        super(ExchangeCreateServiceForm, self).clean()
