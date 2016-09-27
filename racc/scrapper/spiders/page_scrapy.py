from bs4 import BeautifulSoup, Comment
from urlparse import urlparse
import scrapy
from scrapy.linkextractors import LinkExtractor
import re
import os.path
from scrapper.items import PageItem
from scrapy.spiders import SitemapSpider

class BasicPageSpider(SitemapSpider):

    name = 'page'
    allowed_domains = ["racc.edu"]
    sitemap_urls = ['http://www.racc.edu/sitemap.xml']

    def parse(self, response):

        # Parse url to obtain path
        parsed = urlparse(response.url)
        path = parsed.path
        folder = os.path.split(parsed.path)[0]

        # Map url
        mapurl = self.mapuid(path)

        # Beatifulsoup takes over the complete response html
        soup = BeautifulSoup(response.text, 'lxml')

        # Select the content node
        content = soup.find(id="content")
        if content is None:
            item = PageItem()
            item['uid'] = mapurl['uid']
            item['url'] = response.url
            item['path'] = path
            item['folder'] = folder
            yield item

        # remove html comments from it.
        for child in content:
            if isinstance(child, Comment):
                child.extract()

        # Remove the first submenu if it exists
        #menus = content.select(".arrowList")
        #if len(menus) > 0:
            #menus[0].decompose()

        # Remove all top anchors
        top = content.select('a[href^="#top"]')
        for to in top:
            to.decompose()

        # Regex to detect a complete url
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        # Review links
        for a in content.findAll('a', href=True):
            extensionsToCheck = ('.pdf', '.doc', '.xls', '.ppt', 'docx')

            urlCheck = self.mapuid(a['href'])
            if urlCheck['newurl'] == '':
                urlCheck = self.mapuid(folder + '/' + a['href'])

            if urlCheck['newurl'] != '':
                a['href'] = urlCheck['newurl']
            elif regex.match(a['href']):
                a['href'] = a['href']
            elif a['href'].endswith(extensionsToCheck):
                finalasset = folder + '/' + a['href']
                if a['href'][0] == '/':
                    finalasset = a['href']
                a['href'] = '/sites/default/files/imported' + finalasset
            else:
                a['href'] = a['href']

        # Update image urls
        for img in content.findAll('img'):
            if regex.match(img['src']):
                img['src'] = img['src']
            else:
                finalImg = folder + '/' + img['src']
                if img['src'][0] == '/':
                    finalImg = img['src']
                img['src'] = '/sites/default/files/imported' + finalImg

        # Final basic page body as an string, remove linebreaks
        pattern = re.compile(r'\s+')
        body = "".join(str(item) for item in content.contents)
        body = re.sub(pattern, ' ', body).strip()

        item = PageItem()
        item['uid'] = mapurl['uid']
        item['url'] = response.url
        item['path'] = path
        item['folder'] = folder
        item['title'] = response.xpath('//h1/text()').extract_first()
        item['body'] = body

        yield item

    def mapuid(self,key):

        mapuid = {
            'not_exists' : {'uid': '0', 'oldurl': '', 'newurl' : ''},
            '/About/accreditations.aspx': {'uid': '25', 'oldurl': 'About/accreditations.aspx','newurl': '/about-racc/accreditations'},
            '/About/board.aspx': {'uid': '26', 'oldurl': 'About/board.aspx', 'newurl': '/about-racc/board-trustees'},
            '/Business/default.aspx': {'uid': '27', 'oldurl': 'Business/default.aspx', 'newurl': '/about-racc/business-opportunities'},
            '/Foundation/default.aspx': {'uid': '30', 'oldurl': 'Foundation/default.aspx','newurl': '/about-racc/foundation-racc'},
            '/HR/default.aspx': {'uid': '37', 'oldurl': 'HR/default.aspx', 'newurl': '/about-racc/human-resources'},
            '/About/memberships.aspx': {'uid': '44', 'oldurl': 'About/memberships.aspx','newurl': '/about-racc/memberships'},
            '/About/researchGuidelines.aspx': {'uid': '45', 'oldurl': 'About/researchGuidelines.aspx','newurl': '/about-racc/research-guidelines'},
            '/About/smoking-policy.aspx': {'uid': '46', 'oldurl': 'About/smoking-policy.aspx','newurl': '/about-racc/smoketobacco-free'},
            '/About/TitleIX.aspx': {'uid': '47', 'oldurl': 'About/TitleIX.aspx','newurl': '/about-racc/title-ix'},
            '/Foundation/annual.aspx': {'uid': '31', 'oldurl': 'Foundation/annual.aspx', 'newurl': '/about-racc/annual-fund'},
            '/Foundation/donate.aspx': {'uid': '33', 'oldurl': 'Foundation/donate.aspx', 'newurl': '/about-racc/donate'},
            '/Foundation/BOD.aspx': {'uid': '34', 'oldurl': 'Foundation/BOD.aspx','newurl': '/about-racc/foundation-board-directors'},
            '/Foundation/gala.aspx': {'uid': '35', 'oldurl': 'Foundation/gala.aspx','newurl': '/about-racc/gala'},
            '/Foundation/privacy_policy.aspx': {'uid': '36', 'oldurl': 'Foundation/privacy_policy.aspx', 'newurl': '/about-racc/privacy-policy'},
            '/HR/affirm_action.aspx': {'uid': '38', 'oldurl': 'HR/affirm_action.aspx','newurl': '/about-racc/affirmative-action'},
            '/HR/benefits.aspx': {'uid': '39', 'oldurl': 'HR/benefits.aspx','newurl': '/about-racc/benefits'},
            '/HR/logins.aspx': {'uid': '41', 'oldurl': 'HR/logins.aspx','newurl': '/about-racc/employee-logins'},
            '/HR/faq.aspx': {'uid': '42', 'oldurl': 'HR/faq.aspx', 'newurl': '/about-racc/faq'},
            '/HR/application.aspx': {'uid': '43', 'oldurl': 'HR/application.aspx', 'newurl': '/about-racc/job-application'},
            '/Academics/Advising/default.aspx': {'uid': '49', 'oldurl': 'Academics/Advising/default.aspx','newurl': '/academics/academic-advising'},
            '/Academics/enrichment.aspx': {'uid': '50', 'oldurl': 'Academics/enrichment.aspx','newurl': '/academics/academic-enrichment'},
            '/CommunityEd/default.aspx': {'uid': '51', 'oldurl': 'CommunityEd/default.aspx','newurl': '/academics/community-education'},
            '/Academics/ESL/default.aspx': {'uid': '61', 'oldurl': 'Academics/ESL/default.aspx','newurl': '/academics/esl-program'},
            '/Academics/Honors/default.aspx': {'uid': '65', 'oldurl': 'Academics/Honors/default.aspx','newurl': '/academics/honors-program'},
            '/Academics/Health-Professions/default.aspx': {'uid': '76', 'oldurl': 'Academics/Health-Professions/default.aspx','newurl': '/academics/health-professions'},
            '/Online/default.aspx': {'uid': '82','oldurl': 'Online/default.aspx','newurl': '/academics/online-learning'},
            '/STTC/default.aspx': {'uid': '94', 'oldurl': 'STTC/default.aspx','newurl': '/academics/schmidt-training-and-technology-center'},
            '/Academics/technicalAcademy.aspx': {'uid': '119', 'oldurl': 'Academics/technicalAcademy.aspx', 'newurl': '/academics/technical-academy'},
            '/Yocum/default.aspx': {'uid': '120', 'oldurl': 'Yocum/default.aspx','newurl': '/academics/yocum-library'},
            '/CommunityEd/careerTrainProg.aspx': {'uid': '53', 'oldurl': 'CommunityEd/careerTrainProg.aspx', 'newurl': '/academics/career-training-programs'},
            '/CommunityEd/HCPS/commandSpanish.aspx': {'uid': '97', 'oldurl': 'CommunityEd/HCPS/commandSpanish.aspx','newurl': '/academics/command-spanish'},
            '/CommunityEd/register.aspx': {'uid': '55', 'oldurl': 'CommunityEd/register.aspx','newurl': '/academics/course-catalogs-course-registration'},
            '/CommunityEd/GED.aspx': {'uid': '56', 'oldurl': 'CommunityEd/GED.aspx','newurl': '/academics/earn-ged'},
            '/CommunityEd/ESL.aspx': {'uid': '57', 'oldurl': 'CommunityEd/ESL.aspx','newurl': '/academics/esl-programs'},
            '/CommunityEd/HCPS/default.aspx': {'uid': '113', 'oldurl': 'CommunityEd/HCPS/default.aspx','newurl': '/academics/health-care'},
            '/CommunityEd/online_nonCredit.aspx': {'uid': '59', 'oldurl': 'CommunityEd/online_nonCredit.aspx','newurl': '/academics/online-career-training'},
            '/CommunityEd/wits.aspx': {'uid': '60', 'oldurl': 'CommunityEd/wits.aspx','newurl': '/academics/personal-trainer-certification'},
            '/Academics/ESL/courses.aspx': {'uid': '62', 'oldurl': 'Academics/ESL/courses.aspx','newurl': '/academics/esl-courses'},
            '/Academics/ESL/learningCenter.aspx': {'uid': '63', 'oldurl': 'Academics/ESL/learningCenter.aspx','newurl': '/academics/learning-center'},
            '/Academics/ESL/staff.aspx': {'uid': '64', 'oldurl': 'Academics/ESL/staff.aspx','newurl': '/academics/esl-staff'},
            '/Academics/Honors/benefits.aspx': {'uid': '66', 'oldurl': 'Academics/Honors/benefits.aspx','newurl': '/academics/benefits'},
            '/Academics/Honors/credit.aspx': {'uid': '67', 'oldurl': 'Academics/Honors/credit.aspx','newurl': '/academics/earning-honors-credit'},
            '/Academics/Honors/eligible.aspx': {'uid': '68', 'oldurl': 'Academics/Honors/eligible.aspx','newurl': '/academics/eligibility'},
            '/Academics/Honors/faq.aspx': {'uid': '69', 'oldurl': 'Academics/Honors/faq.aspx','newurl': '/academics/faq'},
            '/Academics/Honors/courses.aspx': {'uid': '334', 'oldurl': 'Academics/Honors/courses.aspx','newurl': '/academics/honors-courses'},
            '/Academics/Honors/faculty.aspx': {'uid': '70', 'oldurl': 'Academics/Honors/faculty.aspx','newurl': '/academics/academics/honors-faculty'},
            '/Academics/Honors/committee.aspx': {'uid': '71', 'oldurl': 'Academics/Honors/committee.aspx','newurl': '/academics/honors-committee'},
            '/Academics/Honors/supervise.aspx': {'uid': '72', 'oldurl': 'Academics/Honors/supervise.aspx','newurl': '/academics/supervising-honors-contract'},
            '/Academics/Honors/options.aspx': {'uid': '74', 'oldurl': 'Academics/Honors/options.aspx','newurl': '/academics/program-options'},
            '/Academics/Honors/scholarship.aspx': {'uid': '75', 'oldurl': 'Academics/Honors/scholarship.aspx','newurl': '/academics/academics/scholarships'},
        }

        if key in mapuid:
            return mapuid[key]

        return mapuid['not_exists']

