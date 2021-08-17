import re

from fake_useragent import utils


def get_browsers(verify_ssl=True):
    # https://github.com/hellysmile/fake-useragent/pull/110
    html = utils.get(utils.settings.BROWSERS_STATS_PAGE, verify_ssl=verify_ssl)
    html = html.decode("utf-8")
    html = html.split('<table class="ws-table-all notranslate">')[1]
    html = html.split("</table>")[0]

    pattern = r'\.asp">(.+?)<'
    browsers = re.findall(pattern, html, re.UNICODE)

    browsers = [utils.settings.OVERRIDES.get(browser, browser) for browser in browsers]

    pattern = r'td\sclass="right">(.+?)\s'
    browsers_statistics = re.findall(pattern, html, re.UNICODE)

    return list(zip(browsers, browsers_statistics))
