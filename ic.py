""" Helpers for Imperial based automation.
"""

import sys
import logging

import mechanize


Error = mechanize.URLError


class FormRedirectBrowser(mechanize.Browser):
    def __init__(self, **kwds):
        mechanize.Browser.__init__(self, **kwds)
        self.log = logging.getLogger('Browser')

    def add_password(self, url, user, passwd=None, **kwds):
        """ Add Authorisation for url.
        """
        # Get uri for auth
        uri_parts = url.split('/')
        if uri_parts[0].endswith(':') and uri_parts[1] is '':
            host = uri_parts[2]         # '/'.join(uri_parts[:3])
        else:
            host = uri_parts[0]
        self.log.info("Adding password for user: '{0}', hostname: '{1}'."
                        .format(user, host))
        mechanize.Browser.add_password(self, host, user, passwd, **kwds)

    def redirect_open(self, url, form_name=None, **kwds):
        """ Opens the given URL, then will automaticall try and 'submit()' the 
            form given by 'form_name', until there is no such form.
            Originated due to the habit of imperial EEE to use these forms to 
            attempt to prevent scraping.
        """
        try:
            self.log.info("Browsing to url: '{0}'.".format(url))
            responce = self.open(url, **kwds)
            while True:
                try:
                    if form_name:
                        self.select_form(name=form_name)
                    else:
                        self.select_form(nr=0)
                    self.log.info("Submitting form '{0}' for redirect."
                                    .format(form_name))
                    responce = self.submit()
                except mechanize.FormNotFoundError:
                    break
        except Error as err:
            # If error, report and raise
            self.log.error(str(err))
            raise
        # Return responce body
        return responce


def formopen(url, user=None, passwd=None, form_name=None):
    """ Convinience function to use the FormRedirectBrowser, adding
        authentication as needed.
    """
    browser = FormRedirectBrowser()
    if user:
        browser.add_password(url, user, passwd)
    return browser.redirect_open(url, form_name=form_name)



if __name__ == '__main__':
    sys.stderr.write("Library functions - import only.")
    sys.exit(1)
