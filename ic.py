""" Helpers for Imperial based automation.
"""

import sys
import logging

import mechanize


HTTPError = mechanize.HTTPError


def form_redirect(url, user=None, passwd=None, form_name='t'):
    """ Opens the given URL, then will automaticall try and 'submit()' the 
        form given by 'form_name', until there is no such form.
        Originated due to the habit of imperial EEE to use these forms to 
        attempt to prevent scraping.
    """
    log = logging.getLogger('Browser')
    browser = mechanize.Browser()
    # Add Auth
    if user:
        # Get uri for auth
        uri_parts = url.split('/')
        if uri_parts[0].endswith(':') and uri_parts[1] is '':
            uri = '/'.join(uri_parts[:3])
        else:
            uri = uri_parts[0]
        log.info("Adding password for user: '{0}', uri: '{1}'."
                    .format(user, uri))
        browser.add_password(uri, user, passwd)
    # Try to get responce
    try:
        log.info("Browsing to url: '{0}'.".format(url))
        responce = browser.open(url)
        while True:
            try:
                browser.select_form(name=form_name)
                log.info("Submitting form '{0}' for redirect."
                            .format(form_name))
                responce = browser.submit()
            except mechanize.FormNotFoundError:
                break
    except mechanize.HTTPError as err:
        # If error, report and raise
        log.error(str(err))
        raise
    # Return responce body
    return responce


if __name__ == '__main__':
    sys.stderr.write("Library functions - import only.")
