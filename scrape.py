import config
import lxml.html
import requests
import unicodedata
from lxml.etree import XPath
from itertools import zip_longest

# https://stackoverflow.com/questions/19326004/access-a-function-variable-outside-the-function-without-using-global
def with_this(func):
    def wrapped(*args, **kwargs):
        return func(wrapped, *args, **kwargs)
    return wrapped


@with_this
def scrape(this):
    s = requests.Session()

    # required info
    username = config.username
    password = config.password
    user_id = config.user_id

    # the urls
    base = config.base
    sched = config.sched
    edit_pro = config.edit_pro
    edit_avail = config.edit_avail
    init_side = config.init_side
    init_main = config.init_main

    # Initial custom response header
    headers = {
        'Host': base,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    # Main page custom header
    main_headers = {
        'Host': base,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://' + base + init_main,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    # After logging in: 3 new headers content-type, content-length and referer
    initiated_headers = {
        'Host': base,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '59',
        'Referer': 'https://' + base + init_side,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    # When posting updates to profile
    profile_headers = {
        'Host': base,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '358',
        'Referer': 'https://' + base + edit_pro,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    # When posting updates to availability
    availability_headers = {
        'Host': base,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '11046',
        'Referer': 'https://' + base + edit_avail,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    url = 'https://' + base

    initiate = s.get(url, headers=headers)
    numnum = dict(PHPSESSID=initiate.cookies['PHPSESSID'])

    main = url + '/home.php'
    show_schedule = url + sched + user_id
    unassigned_games = url + sched + '1'
    file_report = url + '/file-report.php'
    edit_profile = url + edit_pro
    edit_availability = url + edit_avail
    contact_list = url + '/contact-list.php'

    payload = {'username': username, 'password': password}

    s.post(url, data=payload, headers=headers, cookies=numnum)

    main_result = s.get(main, headers=main_headers, cookies=numnum)
    schedule_result = s.get(show_schedule, headers=initiated_headers, cookies=numnum)
    unassigned_result = s.get(unassigned_games, headers=initiated_headers, cookies=numnum)
    report_result = s.get(file_report, headers=initiated_headers, cookies=numnum)
    profile_result = s.get(edit_profile, headers=initiated_headers, cookies=numnum)
    avail_result = s.get(edit_availability, headers=initiated_headers, cookies=numnum)
    contact_result = s.get(contact_list, headers=initiated_headers, cookies=numnum)

    main_html = lxml.html.fromstring(main_result.content)
    schedule_html = lxml.html.fromstring(schedule_result.content)
    unassigned_html = lxml.html.fromstring(unassigned_result.content)
    report_html = lxml.html.fromstring(report_result.content)
    profile_html = lxml.html.fromstring(profile_result.content)
    avail_html = lxml.html.fromstring(avail_result.content)
    contact_html = lxml.html.fromstring(contact_result.content)

    scheduler_info_xpath = XPath("//tr/td/font//text()")
    this.scheduler_info = scheduler_info_xpath(main_html)

    rem_spaces = u'\xa0'
    schedule_xpath = XPath("//tr/td/text()")
    this.schedule = schedule_xpath(schedule_html)
    this.schedule_filtered = [unicodedata.normalize('NFKD', rem_spaces).encode('utf-8', 'ignore') for
                              rem_spaces in this.schedule]

    unassigned_xpath = XPath("//tr/td//text()")
    this.unassigned = unassigned_xpath(unassigned_html)
    this.unassigned_filtered = [unicodedata.normalize('NFKD', rem_spaces).encode('utf-8', 'ignore') for
                                rem_spaces in this.unassigned]
    request_xpath = XPath("//tr/td[16]/a/@href")
    this.request = request_xpath(unassigned_html)
    #### Requesting unassigned games ####
    # s.post(edit_profile,
           # data=changes_made,
           # headers=profile_headers, cookies=numnum)

    #### Report Functionality ####
    report_xpath = XPath("//tr/td[8]/a/@href")
    this.report = report_xpath(report_html)

    #### Update work locations ####
    # profile_locs_xpath = XPath("//tr/td/input/checked")
    # this.profile_locs = profile_locs_xpath(profile_html)
    # s.post(edit_profile,
           # data=changes_made,
           # headers=profile_headers, cookies=numnum)

    #### Update available times/days ####
    # avail_xpath = XPath("//tr/td/input/checked")
    # this.avail = avail_xpath(avail_html)
    # s.post(edit_availability,
           # data=changes_made,
           # headers=availability_headers, cookies=numnum)

    info_xpath = XPath("//tr//text()")
    this.info = info_xpath(contact_html)

    last_name_xpath = XPath("//tr/td[1]/text()")
    this.last_names = last_name_xpath(contact_html)

    first_name_xpath = XPath("//tr/td[2]/text()")
    this.first_names = first_name_xpath(contact_html)

    home_xpath = XPath("//tr/td[3]/text()")
    this.home_phone = home_xpath(contact_html)

    cell_xpath = XPath("//tr/td[4]/text()")
    this.cell_phone = cell_xpath(contact_html)

    email_xpath = XPath("//tr/td[5]/text()")
    this.email = email_xpath(contact_html)

    this.info_format = ["{}, {}, {}, {}, {}".format(
        last_name, first_name, home_phone, cell_phone, email) for
        last_name, first_name, home_phone, cell_phone, email in zip_longest(
            this.last_names, this.first_names, this.home_phone, this.cell_phone, this.email)]


if __name__ == '__main__':
    scrape()