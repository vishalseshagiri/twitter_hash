# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for
import scrapy
import matplotlib.pyplot as plt
import os
from PIL import Image
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess
string = ''
count = 0
class QuotesSpider(scrapy.Spider):
    name = "final_try"
    def start_requests(self):
        urls = [
            'https://twitter.com/hashtag/'+str(self.hash_tag),
        ]
        print('Hash tag '+self.hash_tag)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'twit_sense'+self.hash_tag+'.txt'
        global string
        ids = response.xpath('//*[@id="stream-items-id"]/li/@data-item-id').extract()
        print(ids)
        for i in ids:
            temp_string = '//*[@id="stream-item-tweet-'+str(i)+'"]/div/div[2]//text()[re:test(., "\w+")]'
            b = response.xpath(temp_string).extract()
            print(b)
            temp_dict = {}
            temp_dict['Name'] = b[0]
            temp_dict['Handle'] = b[1]
            temp_dict['Date'] = b[2]
            for i in range (4,len(b)):
                if b[i] == 'Embed Tweet':
                    start = i+1
                if 'replies' in b[i]:
                    end = i
                    temp_dict['replies'] = b[i].split(" ")[0]
                if 'retweets' in b[i]:
                    temp_dict['retweets'] = b[i].split(" ")[0]
                if 'likes' in b[i]:
                    temp_dict['likes'] = b[i].split(" ")[0]
            temp_dict['Tweet'] = "".join(b[start:end])
            string = string + str(temp_dict)+"\n"



        with open(filename, 'wb') as f:
            f.write(bytes(string, 'UTF-8'))
        self.log('Saved file %s' % filename)


# Initialize the Flask application
from scrapy.crawler import CrawlerProcess
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('form_submit.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    name=request.form['yourname']
    email=request.form['youremail']
    return render_template('form_action.html', name=name, email=email)

@app.route('/hash_form/')
def hash_form():
    return render_template('hash_form.html')

@app.route('/hash_form_submit/', methods = ['POST'])
def hash_form_submit():
    global string, count
    hash_tag = request.form['hashtag']

    ############################## Working code ##########################
    process = CrawlerProcess()
    process.crawl(QuotesSpider, hash_tag=hash_tag)


    process.start()
        # count = 1
    print("Process started", process)
    process.stop()
    print("Process stopped", process)
    #######################################################################
    # os.chdir("/home/pyth/twitter_hash/tutorial")
    # os.getcwd()
    # os.system("../scrapy crawl final_try -a hash_tag="+hash_tag)
    ##############################This works once too#########################################
    # runner = CrawlerRunner()
    # d = runner.crawl(QuotesSpider, hash_tag=hash_tag)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run() # the script will block here until the crawling is finished
    ############################################################################################
    temp_string = string

    return render_template('hash_form_submit.html', hash_tag = hash_tag, string = str(temp_string))

# Run the app :)
if __name__ == '__main__':
  app.run(
        host="0.0.0.0",
        port=int("8080")
  )
