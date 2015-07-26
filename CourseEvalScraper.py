# https://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python

import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text

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

ids_file = open("course_ids.txt")
ids = ids_file.read().split("\n")
ids_file.close()

output = []
failures = []

for id in ids[:5]:
    print id,
    html = br.open('https://assessment.aas.duke.edu/evaluations/saces/list.php?crse_id=' + id).read()

    soup = BeautifulSoup(html)
    table = soup.find("table")

    if not table:
        print " FAILED"
        failures.append(id)
        continue


    headings = [th.get_text() for th in table.find("tr").find_all("th")]

    datasets = []
    for row in table.find_all("tr")[1:]:
        dataset = (td.get_text() for td in row.find_all("td"))
        datasets.append(dataset)

    for dataset in datasets:
        row = [id, "|"]
        for field in dataset:
            row.append(field)
            row.append("|")
        output.append(''.join(row))

print "\n".join(output)
print "\n".join(failures)

#output_file = open('eval_output.txt', 'w')
#output_file.write("\n".join(output))
#output_file.close()

#failure_output = open('failures.txt', 'w')
#failure_output.write("\n".join(failures))
#failure_output.close()