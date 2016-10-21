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
            '/Business/job_bid.aspx': {'uid': '28', 'newurl': '/about-racc/current-postings'},
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
            '/HR/opportunities.aspx': {'uid': '40', 'newurl': '/about-racc/career-opportunities'},
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
            '/StudentLife/Services/Assessment/apClepDantes.aspx': {'uid': '149', 'newurl': '/admissions/ap-clep-dantes-exams'},
            '/StudentLife/Services/Assessment/credit-by-exam.aspx': {'uid': '151', 'newurl': '/admissions/credit-exam'},
            '/StudentLife/Services/Assessment/careerTech.aspx': {'uid': '152', 'newurl': '/admissions/pa-career-and-technology-centers'},
            '/StudentLife/Services/Assessment/persProfExpCert.aspx': {'uid': '153', 'newurl': '/admissions/personalprofessional-experience-and-certifications'},
            '/StudentLife/Services/Assessment/transferCredit.aspx': {'uid': '154', 'newurl': '/admissions/transfer-credit'},
            '/StudentLife/Services/Assessment/workforceDevelopment.aspx': {'uid': '155', 'newurl': '/admissions/workforce-development-community-education'},
            '/Admissions/Enrollment/default.aspx': {'uid': '156', 'newurl': '/admissions/enrollment'},
            '/Admissions/Enrollment/early.aspx': {'uid': '157', 'newurl': '/admissions/early-admissions'},
            '/Admissions/Enrollment/firstTime.aspx': {'uid': '158', 'newurl': '/admissions/first-time-students'},
            '/Admissions/International/default.aspx': {'uid': '159', 'newurl': '/admissions/international-students'},
            '/Admissions/International/faq.aspx': {'uid': '160', 'newurl': '/admissions/faq'},
            '/Admissions/International/forms.aspx': {'uid': '161', 'newurl': '/admissions/forms'},
            '/Admissions/International/tuition.aspx': {'uid': '162', 'newurl': '/admissions/tuition'},
            '/Admissions/Enrollment/non-degree.aspx': {'uid': '163', 'newurl': '/admissions/non-degree-students'},
            '/Admissions/Enrollment/nursing.aspx': {'uid': '164', 'newurl': '/admissions/nursing-program-students'},
            '/Admissions/Enrollment/returning.aspx': {'uid': '165', 'newurl': '/admissions/returning-students'},
            '/Admissions/Enrollment/disabilities.aspx': {'uid': '166', 'newurl': '/admissions/students-disabilities'},
            '/Admissions/Enrollment/transfer.aspx': {'uid': '167', 'newurl': '/admissions/transfer-students'},
            '/Admissions/Enrollment/Guest.aspx': {'uid': '168', 'newurl': '/admissions/guest-students'},
            '/Admissions/Enrollment/veterans.aspx': {'uid': '203', 'newurl': '/admissions/veterans'},
            '/Admissions/FAQ.aspx': {'uid': '170', 'newurl': '/admissions/faq-0'},

            '/FinancialAid/default.aspx': {'uid': '171', 'newurl': '/admissions/financial-aid'},
            '/FinancialAid/FAQ.aspx': {'uid': '172', 'newurl': '/admissions/financial-aid-faq'},
            '/FinancialAid/terms.aspx': {'uid': '173', 'newurl': '/admissions/financial-aid-terms'},
            '/FinancialAid/timeline.aspx': {'uid': '174', 'newurl': '/admissions/financial-aid-timeline'},
            '/FinancialAid/formsDocs.aspx': {'uid': '175', 'newurl': '/admissions/financial-aid-documents'},
            '/FinancialAid/howTo.aspx': {'uid': '176', 'newurl': '/admissions/how-apply-financial-aid'},
            '/FinancialAid/SAP.aspx': {'uid': '177', 'newurl': '/admissions/sap-and-repeat-classes'},
            '/FinancialAid/Scholarships/default.aspx': {'uid': '178', 'newurl': '/admissions/scholarships'},
            '/FinancialAid/Scholarships/current.aspx': {'uid': '179', 'newurl': '/admissions/racc-scholarships'},
            '/FinancialAid/Scholarships/links.aspx': {'uid': '180', 'newurl': '/admissions/external-scholarships'},
            '/FinancialAid/types.aspx': {'uid': '201', 'newurl': '/admissions/types-financial-aid'},
            '/FinancialAid/veteran.aspx': {'uid': '296', 'newurl': '/admissions/financial-aid-veterans'},
            '/FinancialAid/regulations.aspx': {'uid': '1027', 'newurl': '/admissions/rights-and-responsibilities'},
            '/FinancialAid/Workstudy/default.aspx': {'uid': '204', 'newurl': '/admissions/work-study'},
            '/FinancialAid/Workstudy/job_opp.aspx': {'uid': '205', 'newurl': '/admissions/job-opportunities'},
            '/FinancialAid/Workstudy/pay_dates.aspx': {'uid': '206', 'newurl': '/admissions/pay-schedule-logins'},
            '/FinancialAid/Workstudy/faq.aspx': {'uid': '207', 'newurl': '/admissions/work-study-faqs'},
            '/Orientation/default.aspx': {'uid': '208', 'newurl': '/admissions/orientation'},
            '/Admissions/Placement/default.aspx': {'uid': '209', 'newurl': '/admissions/placement-testing'},
            '/Admissions/Placement/placement_prep.aspx': {'uid': '210', 'newurl': '/admissions/test-preparation'},
            '/Admissions/Placement/placement_waiver.aspx': {'uid': '211', 'newurl': '/admissions/placement-test-waivers'},
            '/Admissions/Placement/retesting.aspx': {'uid': '212', 'newurl': '/admissions/retesting-policy'},
            '/Ravens/default.aspx': {'uid': '213', 'newurl': '/admissions/raven-ambassadors'},
            '/Ravens/ambassadors.aspx': {'uid': '214', 'newurl': '/admissions/meet-ambassadors'},
            '/Admissions/staff.aspx': {'uid': '215', 'newurl': '/admissions/staff'},
            '/Transfer/default.aspx': {'uid': '216', 'newurl': '/admissions/transfer-services'},
            '/Transfer/college-visits.aspx': {'uid': '217', 'newurl': '/admissions/college-visits'},
            '/Transfer/crossReg.aspx': {'uid': '218', 'newurl': '/admissions/cross-registration'},
            '/Transfer/crossRegFAQ.aspx': {'uid': '219', 'newurl': '/admissions/cross-registration-faq'},
            '/Admissions/DualAdmissions/default.aspx': {'uid': '220', 'newurl': '/admissions/dual-admissions'},
            '/Admissions/DualAdmissions/albright.aspx': {'uid': '190', 'newurl': '/admissions/albright'},
            '/Admissions/DualAdmissions/alvernia.aspx': {'uid': '191', 'newurl': '/admissions/alvernia'},
            '/Admissions/DualAdmissions/bloomsburg.aspx': {'uid': '192', 'newurl': '/admissions/bloomsburg'},
            '/Admissions/DualAdmissions/kutztown.aspx': {'uid': '193', 'newurl': '/admissions/kutztown'},
            '/Admissions/DualAdmissions/millersville.aspx': {'uid': '194', 'newurl': '/admissions/millersville'},
            '/Admissions/DualAdmissions/stjosephs.aspx': {'uid': '195', 'newurl': '/admissions/st-josephs'},
            '/Admissions/DualAdmissions/temple.aspx': {'uid': '196', 'newurl': '/admissions/temple'},
            '/Transfer/terms.aspx': {'uid': '222', 'newurl': '/admissions/glossary-transfer'},
            '/Transfer/faq.aspx': {'uid': '223', 'newurl': '/admissions/transfer-services-faq'},
            '/Transfer/Guides/default.aspx': {'uid': '224', 'newurl': '/admissions/transfer-guides'},
            '/Transfer/planning.aspx': {'uid': '225', 'newurl': '/admissions/transfer-planning'},
            '/Transfer/scholarships.aspx': {'uid': '181', 'newurl': '/admissions/transfer-scholarships'},
            '/Transfer/Guides/schools.aspx': {'uid': '183', 'newurl': '/admissions/berks-county-schools'},
            '/Transfer/Guides/health.aspx': {'uid': '184', 'newurl': '/admissions/health-science-programs'},
            '/Transfer/Guides/online.aspx': {'uid': '185', 'newurl': '/admissions/online-universities'},
            '/Transfer/Guides/pa-schools.aspx': {'uid': '186', 'newurl': '/admissions/other-pa-schools'},
            '/Transfer/Guides/stem.aspx': {'uid': '187', 'newurl': '/admissions/stem-programs'},
            '/Transfer/TCED.aspx': {'uid': '227', 'newurl': '/admissions/transfer-course-equivalency-database'},
            '/Tuition/tuitionFees.aspx': {'uid': '228', 'newurl': '/admissions/tuition-and-fees'},
            '/Tuition/default.aspx': {'uid': '229', 'newurl': '/admissions/cashiers-office'},
            '/Tuition/dereg.aspx': {'uid': '230', 'newurl': '/admissions/deregistration'},
            '/Tuition/paymentInfo.aspx': {'uid': '231', 'newurl': '/admissions/payment-information'},
            '/Tuition/refund.aspx': {'uid': '232', 'newurl': '/admissions/refunds-and-adjustments'},


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

