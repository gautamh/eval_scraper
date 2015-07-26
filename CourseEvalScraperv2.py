# https://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python

import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text
import re
import itertools
from urlparse import parse_qs, urlparse

import globals

br = mechanize.Browser()
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)


br.addheaders = [('User-agent', 'Chrome')]

br.open('https://assessment.trinity.duke.edu/evaluations/saces/index.php')

#for f in br.forms():
#    print f

br.select_form(nr=0)

# User credentials
br.form['j_username'] = globals.username
br.form['j_password'] = globals.password

# Login
br.submit()

br.open('https://assessment.aas.duke.edu/evaluations/saces/list.php?crse_id=005833')
br.select_form(nr=0)
br.submit()

ids_file = open("course_ids_unique.txt")
ids = ids_file.read().split("\n")
ids_file.close()

output = []
failures = []

output_file = open('eval_output5.txt', 'a')
failure_output = open('failures5.txt', 'a')
for id in ids:
    try:
        print id,
        #navigate to evaluation page for current id
        html = br.open('https://assessment.aas.duke.edu/evaluations/saces/list.php?crse_id=' + id).read()

        soup = BeautifulSoup(html) #input to bs4
        table = soup.find("table") #find ratings table

        if not table: #handle courses without ratings
            print " FAILED"
            #failures.append(id)
            failure_output.write(id)
            if html:
                if "database error" in html:
                    failure_output.write(" database error")
            failure_output.write("\n")
            continue


        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        datasets = []
        class_links = br.links(url_regex="eval.php?") #find class detail links

        #go through table rows and class detail links
        for row, link in zip(table.find_all("tr")[1:], class_links): #extract data
            dataset = list((td.get_text() for td in row.find_all("td")))
            class_html = br.follow_link(link)
            query_params = parse_qs(urlparse(class_html.geturl()).query, keep_blank_values=True)
            class_nbr = query_params['class_nbr']
            dataset.append(class_nbr[0])
            try:
                class_soup = BeautifulSoup(class_html)
            except httplib.IncompleteRead, e:
                class_soup = BeautifulSoup(e.partial)
            class_table = class_soup.find(id="datapage")

            #extract response number data
            scripts = class_soup.find_all("script")
            if len(scripts) > 3:
                found = re.search("\] = '(.+?)';", scripts[3].text).group(1)
                soup3 = BeautifulSoup(found)
                script_table = soup3.find("table")
                for class_total in script_table.find_all("tr")[7:9]:
                    addition = list(class_total.children)[1].text
                    dataset.append(addition)
            br.back()

            datasets.append(dataset)

        #merge data for course and output
        for dataset in datasets:
            row = [id, "|"]
            for field in dataset:
                row.append(field)
                row.append("|")
            output_file.write(''.join(row))
            output_file.write("\n")

        print "\n",
    except BaseException as e:
        print e.message
        print e.args
        print " FAILED (EXCEPTION)"
            #failures.append(id)
        failure_output.write(id)
        #output.append(''.join(row))

#print "\n".join(output)
#print "\n".join(failures)


output_file.close()

#failure_output.write("\n".join(failures))
failure_output.close()