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
            extensionsToCheck = ('.pdf', '.doc', '.xls', '.ppt', 'docx', 'xlsx', 'pptx', 'zip', 'rar')

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
            'not_exists' : {'uid': '0', 'newurl' : ''},

            '/About/accreditations.aspx': {'uid': '25','newurl': '/about-racc/accreditations'},
            '/About/board.aspx': {'uid': '26', 'newurl': '/about-racc/board-trustees'},
            '/Business/default.aspx': {'uid': '27', 'newurl': '/about-racc/business-opportunities'},
            '/Foundation/default.aspx': {'uid': '30', 'newurl': '/about-racc/foundation-racc'},
            '/HR/default.aspx': {'uid': '37', 'newurl': '/about-racc/human-resources'},
            '/About/memberships.aspx': {'uid': '44', 'newurl': '/about-racc/memberships'},
            '/About/researchGuidelines.aspx': {'uid': '45', 'newurl': '/about-racc/research-guidelines'},
            '/About/smoking-policy.aspx': {'uid': '46', 'newurl': '/about-racc/smoketobacco-free'},
            '/About/TitleIX.aspx': {'uid': '47', 'newurl': '/about-racc/title-ix'},
            '/Foundation/annual.aspx': {'uid': '31', 'newurl': '/about-racc/annual-fund'},
            '/Foundation/donate.aspx': {'uid': '33', 'newurl': '/about-racc/donate'},
            '/Foundation/BOD.aspx': {'uid': '34', 'newurl': '/about-racc/foundation-board-directors'},
            '/Foundation/gala.aspx': {'uid': '35', 'newurl': '/about-racc/gala'},
            '/Foundation/privacy_policy.aspx': {'uid': '36', 'newurl': '/about-racc/privacy-policy'},
            '/HR/affirm_action.aspx': {'uid': '38', 'newurl': '/about-racc/affirmative-action'},
            '/HR/benefits.aspx': {'uid': '39', 'newurl': '/about-racc/benefits'},
            '/HR/logins.aspx': {'uid': '41', 'newurl': '/about-racc/employee-logins'},
            '/HR/faq.aspx': {'uid': '42', 'newurl': '/about-racc/faq'},
            '/HR/application.aspx': {'uid': '43', 'newurl': '/about-racc/job-application'},

            '/Academics/Advising/default.aspx': {'uid': '49', 'newurl': '/academics/academic-advising'},
            '/Academics/enrichment.aspx': {'uid': '50', 'newurl': '/academics/academic-enrichment'},
            '/Academics/technicalAcademy.aspx': {'uid': '119', 'newurl': '/academics/technical-academy'},

            '/CommunityEd/default.aspx': {'uid': '51', 'newurl': '/academics/community-education'},
            '/CommunityEd/careerTrainProg.aspx': {'uid': '53', 'newurl': '/academics/career-training-programs'},
            '/CommunityEd/HCPS/commandSpanish.aspx': {'uid': '97', 'newurl': '/academics/command-spanish'},
            '/CommunityEd/register.aspx': {'uid': '55', 'newurl': '/academics/course-catalogs-course-registration'},
            '/CommunityEd/GED.aspx': {'uid': '56', 'newurl': '/academics/earn-ged'},
            '/CommunityEd/ESL.aspx': {'uid': '57', 'newurl': '/academics/esl-programs'},
            '/CommunityEd/HCPS/default.aspx': {'uid': '113', 'newurl': '/academics/health-care'},
            '/CommunityEd/online_nonCredit.aspx': {'uid': '59', 'newurl': '/academics/online-career-training'},
            '/CommunityEd/wits.aspx': {'uid': '60', 'newurl': '/academics/personal-trainer-certification'},

            '/Academics/ESL/default.aspx': {'uid': '61', 'newurl': '/academics/esl-program'},
            '/Academics/ESL/courses.aspx': {'uid': '62', 'newurl': '/academics/esl-courses'},
            '/Academics/ESL/learningCenter.aspx': {'uid': '63', 'newurl': '/academics/learning-center'},
            '/Academics/ESL/staff.aspx': {'uid': '64', 'newurl': '/academics/esl-staff'},

            '/Academics/Honors/default.aspx': {'uid': '65', 'newurl': '/academics/honors-program'},
            '/Academics/Honors/benefits.aspx': {'uid': '66', 'newurl': '/academics/benefits'},
            '/Academics/Honors/credit.aspx': {'uid': '67', 'newurl': '/academics/earning-honors-credit'},
            '/Academics/Honors/eligible.aspx': {'uid': '68', 'newurl': '/academics/eligibility'},
            '/Academics/Honors/faq.aspx': {'uid': '69', 'newurl': '/academics/faq'},
            '/Academics/Honors/courses.aspx': {'uid': '334', 'newurl': '/academics/honors-courses'},
            '/Academics/Honors/faculty.aspx': {'uid': '70', 'newurl': '/academics/academics/honors-faculty'},
            '/Academics/Honors/committee.aspx': {'uid': '71', 'newurl': '/academics/honors-committee'},
            '/Academics/Honors/supervise.aspx': {'uid': '72', 'newurl': '/academics/supervising-honors-contract'},
            '/Academics/Honors/options.aspx': {'uid': '74', 'newurl': '/academics/program-options'},
            '/Academics/Honors/scholarship.aspx': {'uid': '75', 'newurl': '/academics/academics/scholarships'},

            '/Academics/Health-Professions/default.aspx': {'uid': '76', 'newurl': '/academics/health-professions'},
            '/Academics/Health-Professions/MLT-Program.aspx': {'uid': '77','newurl': '/academics/medical-laboratory-technician'},
            '/Academics/Health-Professions/Nursing-Program.aspx': {'uid': '78','newurl': '/academics/nursing-program'},
            '/Academics/Health-Professions/Practical-Nursing.aspx': {'uid': '79', 'newurl': '/academics/practical-nursing'},
            '/Academics/Health-Professions/Respiratory-Care.aspx': {'uid': '80', 'newurl': '/academics/respiratory-care'},
            '/Academics/Health-Professions/sna.aspx': {'uid': '81', 'newurl': '/academics/student-nurses-association'},

            '/Online/default.aspx': {'uid': '82', 'newurl': '/academics/online-learning'},
            '/Online/alternateExamLocations.aspx': {'uid': '91', 'newurl': '/academics/alternate-campus-exam-locations'},
            '/Canvas/default.aspx': {'uid': '83', 'newurl': '/academics/canvas'},
            '/Canvas/collaborate.aspx': {'uid': '84', 'newurl': '/academics/collaborate'},
            '/Canvas/faculty-resources.aspx': {'uid': '85', 'newurl': '/academics/faculty-resources'},
            '/Canvas/student-resources.aspx': {'uid': '86', 'newurl': '/academics/student-resources'},
            '/Online/contacts.aspx': {'uid': '566', 'newurl': '/academics/contacts'},
            '/Online/identity.aspx': {'uid': '88', 'newurl': '/academics/identity-verification-procedures'},
            '/Online/credit.aspx': {'uid': '89', 'newurl': '/academics/online-courses-credit'},
            '/Online/off-CampusExamProcedures.aspx': {'uid': '90', 'newurl': '/academics/campus-exam-procedure'},
            '/Online/online_success.aspx': {'uid': '92', 'newurl': '/academics/online-success'},

            '/STTC/default.aspx': {'uid': '94', 'newurl': '/academics/schmidt-training-and-technology-center'},
            '/STTC/ManufacturingTech/AMIST.aspx': {'uid': '95', 'newurl': '/academics/advanced-material-integrated-systems-technology-amis'},
            '/STTC/InformationTech/default.aspx': {'uid': '100', 'newurl': '/academics/information-technology'},
            '/STTC/InformationTech/ITCareers.aspx': {'uid': '101', 'newurl': '/academics/it-training'},
            '/STTC/ManufacturingTech/default.aspx': {'uid': '104', 'newurl': '/academics/manufacturing-technology'},
            '/STTC/ManufacturingTech/mechanical.aspx': {'uid': '105', 'newurl': '/academics/mechanical'},
            '/STTC/ManufacturingTech/mechatronics.aspx': {'uid': '106', 'newurl': '/academics/mechatronics'},
            '/STTC/ManufacturingTech/manufacturing.aspx': {'uid': '107', 'newurl': '/academics/manufacturing-processes'},
            '/STTC/ManufacturingTech/progammable.aspx': {'uid': '108', 'newurl': '/academics/programmable-logic-controller-plc'},
            '/STTC/water.aspx': {'uid': '109', 'newurl': '/academics/wastewater-treatment-plant-operator'},
            '/STTC/workforce.aspx': {'uid': '111', 'newurl': '/academics/workforce-development'},
            '/CommunityEd/HCPS/default.aspx': {'uid': '568', 'newurl': '/academics/health-care-0'},
            '/CommunityEd/HCPS/instructorCourse.aspx': {'uid': '114', 'newurl': '/academics/american-heart-association-bls'},
            '/CommunityEd/HCPS/cpr.aspx': {'uid': '115', 'newurl': '/academics/heartsaver-instructor-course'},
            '/CommunityEd/HCPS/BLS.aspx': {'uid': '116', 'newurl': '/academics/bls-courses-healthcare-professionals'},
            '/CommunityEd/HCPS/IVCertification.aspx': {'uid': '117', 'newurl': '/academics/iv-venipuncture-certification'},
            '/CommunityEd/ABE.aspx': {'uid': '118', 'newurl': '/academics/adult-basic-education'},

            '/Yocum/default.aspx': {'uid': '120', 'newurl': '/academics/yocum-library'},
            '/Yocum/about.aspx': {'uid': '121', 'newurl': '/academics/about-library'},
            '/Yocum/testing.aspx': {'uid': '122', 'newurl': '/academics/academic-testing-center'},
            '/Yocum/lib-books-films.aspx': {'uid': '123', 'newurl': '/academics/e-books'},
            '/Yocum/lib-faculty.aspx': {'uid': '124', 'newurl': '/academics/library-services-faculty-and-staff'},
            '/Yocum/lib-student.aspx': {'uid': '315', 'newurl': '/academics/library-services-students'},
            '/Yocum/MLA_APA_Guides.aspx': {'uid': '125', 'newurl': '/academics/mla-and-apa-guides'},
            '/Yocum/onlineDatabases/default.aspx': {'uid': '316', 'newurl': '/academics/online-databases'},
            '/Yocum/onlineDatabases/databasesA-Z.aspx': {'uid': '126', 'newurl': '/academics/z-databases'},
            '/Yocum/onlineDatabases/allsubjects.aspx': {'uid': '127', 'newurl': '/academics/all-subjects'},
            '/Yocum/onlineDatabases/art-music-images.aspx': {'uid': '128', 'newurl': '/academics/all-subjectsart-music-and-media'},
            '/Yocum/onlineDatabases/business.aspx': {'uid': '129', 'newurl': '/academics/business'},
            '/Yocum/onlineDatabases/diversity.aspx': {'uid': '130', 'newurl': '/academics/diversity'},
            '/Yocum/onlineDatabases/education.aspx': {'uid': '131', 'newurl': '/academics/education'},
            '/Yocum/onlineDatabases/health.aspx': {'uid': '132', 'newurl': '/academics/health-and-science'},
            '/Yocum/onlineDatabases/history.aspx': {'uid': '133', 'newurl': '/academics/history'},
            '/Yocum/onlineDatabases/lang-lit.aspx': {'uid': '134', 'newurl': '/academics/literature-and-philosophy'},
            '/Yocum/onlineDatabases/social-sciences.aspx': {'uid': '135', 'newurl': '/academics/social-sciences'},
            '/Yocum/special_collections.aspx': {'uid': '136', 'newurl': '/academics/special-collections'},
            '/Yocum/UsefulLinks/default.aspx': {'uid': '137', 'newurl': '/academics/useful-links'},
            '/Yocum/UsefulLinks/business.aspx': {'uid': '138', 'newurl': '/academics/business-and-careers'},
            '/Yocum/UsefulLinks/genealogy.aspx': {'uid': '139', 'newurl': '/academics/genealogy'},
            '/Yocum/UsefulLinks/gov.aspx': {'uid': '140', 'newurl': '/academics/government'},
            '/Yocum/UsefulLinks/health.aspx': {'uid': '141', 'newurl': '/academics/health'},
            '/Yocum/UsefulLinks/history.aspx': {'uid': '142', 'newurl': '/academics/history-0'},
            '/Yocum/UsefulLinks/tools.aspx': {'uid': '143', 'newurl': '/academics/internet-tools'},
            '/Yocum/UsefulLinks/library.aspx': {'uid': '144', 'newurl': '/academics/library'},
            '/Yocum/UsefulLinks/literature.aspx': {'uid': '145', 'newurl': '/academics/literature'},
            '/Yocum/UsefulLinks/reference.aspx': {'uid': '146', 'newurl': '/academics/reference'},

            '/StudentLife/Services/Assessment/default.aspx': {'uid': '148', 'newurl': '/admissions/assessment-services'},
            '/Admissions/Enrollment/default.aspx': {'uid': '156', 'newurl': '/admissions/enrollment'},
            '/Admissions/FAQ.aspx': {'uid': '170', 'newurl': '/admissions/faq-0'},
            '/FinancialAid/default.aspx': {'uid': '171', 'newurl': '/admissions/financial-aid'},
            '/Orientation/default.aspx': {'uid': '208', 'newurl': '/admissions/orientation'},
            '/Admissions/Placement/default.aspx': {'uid': '209', 'newurl': '/admissions/placement-testing'},
            '/Ravens/default.aspx': {'uid': '213', 'newurl': '/admissions/raven-ambassadors'},
            '/Admissions/staff.aspx': {'uid': '215', 'newurl': '/admissions/staff'},
            '/Transfer/default.aspx': {'uid': '216', 'newurl': '/admissions/transfer-services-0'},
            '/Tuition/default.aspx': {'uid': '228', 'newurl': '/admissions/tuition-and-fees'},
            '/StudentLife/Clubs/default.aspx': {'uid': '233', 'newurl': '/student-life/clubs-and-organizations'},
            '/StudentLife/Services/FitnessCenter/default.aspx': {'uid': '235', 'newurl': '/student-life/fitness-center'},
            '/StudentLife/leadership.aspx': {'uid': '236', 'newurl': '/student-life/leadership-program'},
            '/StudentLife/RACCy/default.aspx': {'uid': '237', 'newurl': '/student-life/raccy-olympics'},
            '/Academics/catalogs.aspx': {'uid': '238', 'newurl': '/student-life/student-handbook'},

            '/StudentLife/Services/default.aspx': {'uid': '239', 'newurl': '/student-life/clubs-and-organizations'},
            '/About/Directions/campusmap.aspx': {'uid': '303', 'newurl': '/contacts/campus-map-and-directions'},
            '/About/Directions/default.aspx': {'uid': '307', 'newurl': '/contacts/main-campus-directions'},
            '/About/Directions/offSite.aspx': {'uid': '308', 'newurl': '/contacts/campus-map-and-directions'},
            '/IT/default.aspx': {'uid': '304', 'newurl': '/contacts/information-services'},
            '/IT/contact_info.aspx': {'uid': '309', 'newurl': '/contacts/contact-it-staff'},
            '/IT/lab_hours.aspx': {'uid': '310', 'newurl': '/contacts/computer-lab-hours'},
            '/IT/computer_policy.aspx': {'uid': '311', 'newurl': '/contacts/computer-usage-policy'},
            '/IT/faculty_staff.aspx': {'uid': '312', 'newurl': '/contacts/faculty-and-staff'},
            '/IT/web_support.aspx': {'uid': '313', 'newurl': '/contacts/website-support'},
            '/Safety/default.aspx': {'uid': '306', 'newurl': '/contacts/safety-security'},
        }

        if key in mapuid:
            return mapuid[key]

        return mapuid['not_exists']

