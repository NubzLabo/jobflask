from flask import Flask, render_template, request, redirect, url_for, session, Response
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup as bs
import unicodedata, time
import re

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "saucysecretkey"

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        session["job"] = str(request.form["job"].replace(" ","-"))
        session["loc"] = str(request.form["loc"].replace(" ","-"))
        return redirect(url_for("get_search_result"))
   
    else:

        url = "https://www.jobstreet.com.my/en/job-search/job-vacancy.php?ojs=1/"

        response = rq.get(url)

        soup = bs(response.text, "html.parser")

        card = soup.find_all("div", "sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu")

        select_page = soup.findAll("option")
        total_job = soup.find_all("span", "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvc8")

        total_job_str = str(total_job[0])
        total_job_final = re.search("of (.*) jobs",total_job_str).group(1)

        total_card = len(card)
        max_page = int(select_page[-1].get("value"))
        total_max_page = f"{max_page:,d}"

        return render_template("home.html", card=total_card, page=total_max_page, total=total_job_final)

@app.route("/search_result", methods=["GET","POST"])
def get_search_result():

    if request.method == "POST":
        session["page"] = request.form["page"]
        return redirect(url_for("return_page_result"))

    else:
        
        job = session.get("job")
        loc = session.get("loc")

        if job != "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs-in-{loc}/"
        elif job != "" and loc == "":    
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs/"
        elif job == "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{loc}-jobs/"
        elif job == "" and loc == "":
            url = "https://www.jobstreet.com.my/en/job-search/job-vacancy.php"
        
        response = rq.get(url)
        
        soup = bs(response.text, "html.parser")

        card = soup.find_all("div", "sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu")

        select_page = soup.findAll("option")
        
        try:
            total_card = len(card)
            max_page = int(select_page[-1].get("value"))
            total_max_page = f"{max_page:,d}"
            total_job = soup.find_all("span", "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvc8")

            total_job_str = str(total_job[0])
            total_job_final = re.search("of (.*) jobs",total_job_str).group(1)

            got_exc = True
            return render_template("search_result.html", job=job, loc=loc, card=total_card, maxpage=max_page, page=total_max_page, total=total_job_final, exc=got_exc)
        
        except:
            got_exc = False
            return render_template("search_result.html", job=job, loc=loc, exc=got_exc)

@app.route("/final_result", methods=["GET","POST"])
def return_page_result():
        record = []

        job = session.get("job")
        loc = session.get("loc")
        pageint = int(session.get("page"))

        if job != "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs-in-{loc}/"
        elif job != "" and loc == "":    
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs/"
        elif job == "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{loc}-jobs/"
        elif job == "" and loc == "":
            url = "https://www.jobstreet.com.my/en/job-search/job-vacancy.php"

        response = rq.get(url)
        soup = bs(response.text, "html.parser")
        card = soup.find_all("div", "sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu")
        select_page = soup.findAll("option")

        total_card = len(card)
        max_page = int(select_page[-1].get("value"))
        total_max_page = f"{max_page:,d}"
        total_job = soup.find_all("span", "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvc8")

        total_job_str = str(total_job[0])
        total_job_final = re.search("of (.*) jobs",total_job_str).group(1)

        final_url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs-in-{loc}/{{}}"

        url_page = [final_url.format(i) for i in range(1, pageint+1)]
        
        if pageint <= max_page:
            for url in url_page:
                for all_card in card:
                    job_detail = get_job(all_card)
                    record.append(job_detail)

        col = ["Job Name", "Company Name", "Job Location", "Salary", "Job Summary", "Post Date", "Job Url"]

        job_street_data = pd.DataFrame(record, columns=col)

        job_street_html = job_street_data.to_html()

        got_exc = True
        return render_template("final_result.html", data=job_street_html, job=job, loc=loc, exc=got_exc, inputpage=pageint, card=total_card, maxpage=max_page, page=total_max_page, total=total_job_final)

@app.route("/output", methods=["GET","POST"])
def save_result():
    if request.method == "POST":
        record = []

        job = session.get("job")
        loc = session.get("loc")
        pagestr = str(session.get("page"))
        pageint = int(session.get("page"))
        timestr = time.strftime("%Y%m%d-%H%M%S")

        if job != "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs-in-{loc}/"
        elif job != "" and loc == "":    
            url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs/"
        elif job == "" and loc != "":
            url = f"https://www.jobstreet.com.my/en/job-search/{loc}-jobs/"
        elif job == "" and loc == "":
            url = "https://www.jobstreet.com.my/en/job-search/job-vacancy.php"

        response = rq.get(url)
        soup = bs(response.text, "html.parser")
        card = soup.find_all("div", "sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu")

        select_page = soup.findAll("option")
        max_page = int(select_page[-1].get("value"))

        final_url = f"https://www.jobstreet.com.my/en/job-search/{job}-jobs-in-{loc}/{{}}"

        url_page = [final_url.format(i) for i in range(1, pageint+1)]
        
        if pageint <= max_page:
            for url in url_page:
                for all_card in card:
                    job_detail = get_job(all_card)
                    record.append(job_detail)

        col = ["Job Name", "Company Name", "Job Location", "Salary", "Job Summary", "Post Date", "Job Url"]

        job_street_data = pd.DataFrame(record, columns=col)

        csv_data = job_street_data.to_csv(index=True, encoding="utf-8")

        csv_fname = f"js_data_page1-{pagestr}_{timestr}.csv"

        return Response(csv_data, mimetype="text/csv", headers={"Content-disposition":"attachment; filename=" + csv_fname})

def get_job(card):
	jobname = card.find("span", "sx2jih0").text.strip()  # find single info? use find(), multiple info? use find.all()

	try:
		coname = card.find("span", "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _18qlyvca").text.strip()
	except:
		coname = "Company Confidential"

	anchortag = card.a  # use a to get anchortag
	joburl = "https://www.jobstreet.com.my" + anchortag.get("href")  # from this anchor tag get href attribute

	jobloc = card.find("span", "sx2jih0 zcydq84u zcydq80 iwjz4h0").text.strip()

	try:
		jobsummary = card.find("ul","sx2jih0 sx2jih3 _17fduda0 _17fduda5")  # with .text it will produce an error if empty
		savelitext = ""
		if jobsummary.text != "":
			for allli in jobsummary("li"):
				litagtext = allli.text
				savelitext = savelitext + litagtext + ", "
				jobsum = savelitext.rstrip(", ")
		else:
			jobsum = "no job summary"
	except:
		jobsum = "no job summary"

	jobsalary = card.find_all("span","sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc3 _18qlyvc7")  # if >2, scrap from index [1]
	try:
		if len(jobsalary) >= 2:
			jobsalary = jobsalary[1].text.strip()
			jobsal = unicodedata.normalize("NFKD", jobsalary) # trim
		else:
			jobsal = "no salary info"
	except:
		jobsal = "error-no salary info"

	timetag = card.time
	postdate = timetag.get("datetime")
	postdate = postdate.split("T", 1)
	postdate = postdate[0]

	jobinfo = (jobname, coname, jobloc,  jobsal, jobsum, postdate, joburl)
	return jobinfo

if __name__ == "__main__":
    app.run(
    host='0.0.0.0',
    debug = True,
    port=8080
  )

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')   
    return response