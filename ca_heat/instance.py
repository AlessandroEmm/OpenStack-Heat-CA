# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from heat.engine import scheduler
from heat.engine.resources import nova_utils
import heat.engine.resources.instance

from heat.common import exception

from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging

from OpenSSL import crypto
from certgen import * 
import os
import base64
import urllib2

logger = logging.getLogger(__name__)


class Instance(heat.engine.resources.instance.Instance):
    tags_schema = {'Key': {'Type': 'String',
                           'Required': True},
                   'Value': {'Type': 'String',
                             'Required': True}}

    properties_schema = {'ca-pkcs12' : {'Type': 'String',
                                     'Required': True},
                        'ca-password' : {'Type': 'String',
                                     'Required': True},
                        'cert-cname' : {'Type': 'String',
                                     'Required': True},
                        'genCA' : {'Type': 'Boolean',
                                    'Default': False,
                                     'Required': True}

                                     }


    attributes_schema = {'ServerPKCS12': ('PKCS12 as base64'),
                         'CA': ('Certificate an PKey in PKCS12 as base64')}

    update_allowed_keys = ('Metadata', 'Properties')
    update_allowed_properties = None
    myAttributes = {}

    def __init__(self, name, json_snippet, stack):
        super(Instance, self).__init__(name, json_snippet, stack)

    def _getFile(self, path):
        if path.startswith("http") or path.startswith("https"):
            try:
                p12 = urllib2.urlopen(path).read()
                return p12
            except urllib2.URLError:
                return None
        else:
            if os.path.isfile(path):
                return open(path).read()
            else: return None

    def _generateServerCert(self, pkcs12):
        pkey = createKeyPair(TYPE_RSA, 2048)
        req = createCertRequest(pkey, CN=self.properties['cert-cname'])
        cert = createCertificate(req, (pkcs12.get_certificate(), pkcs12.get_privatekey()), 1, (0, 60*60*24*365*5)) # five years
        return (pkey, cert)

    def _buildPKCS12(self, pkey, cert, cas):
        serverPKCS12 = crypto.PKCS12()
        serverPKCS12.set_privatekey( pkey )
        serverPKCS12.set_certificate( cert ) 
        serverPKCS12.set_ca_certificates(cas)
        return serverPKCS12

    def _mergeCAChain(self, certList, cert):
        if not certList:
            return [ cert ]
        else:
            return certList.append(cert)



    def handle_create(self):
        pkcs12Path = self._getFile(self.properties['ca-pkcs12'])
        if self._getFile(self.properties['ca-pkcs12']):
            pkcs12 = crypto.load_pkcs12(pkcs12Path, self.properties['ca-password'])
            (pkey, cert) = self._generateServerCert(pkcs12)
            serverPKCS12 = self._buildPKCS12(pkey, cert, self._mergeCAChain(pkcs12.get_ca_certificates(), pkcs12.get_certificate()))
            self.myAttributes['ServerPKCS12'] = base64.b64encode(serverPKCS12.export())
            logger.debug(serverPKCS12.get_certificate().get_issuer() )
            logger.debug(serverPKCS12.get_certificate().get_subject() )
            return self.myAttributes['ServerPKCS12']
        elif  self.properties['ca-pkcs12']:
            return None
        else:
            # pkey = createKeyPair(TYPE_RSA, 1024)
            # req = createCertRequest(pkey, CN=cname)       
            return None

    def check_create_complete(self, cookie):
        if not cookie:
            raise Exception('No CA and no instructions for building one either')
        else:
            pkcs12 = crypto.load_pkcs12(base64.b64decode(cookie), "")
            logger.debug(pkcs12.get_certificate().get_subject() == crypto.load_pkcs12(base64.b64decode(self.myAttributes['ServerPKCS12'])).get_certificate().get_subject())
            return pkcs12.get_certificate().get_subject() == crypto.load_pkcs12(base64.b64decode(self.myAttributes['ServerPKCS12'])).get_certificate().get_subject()

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass

    def _resolve_attribute(self, name):
        return self.myAttributes[name]



def resource_mapping():
    return {
        'Sec::Certificate::Client': Instance,
    }
