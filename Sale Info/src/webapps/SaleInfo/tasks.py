from celery.task.schedules import crontab
from celery.decorators import periodic_task

from lxml import html
import requests

import re

from SaleInfo.models import *

@periodic_task(run_every=(crontab(minute='*/1')), name="some_task", ignore_result=True)
def some_task():
    brands = Brand.objects.all()
    # iterate each brand to parse its html and get the information
    for brand in brands:
        page = requests.get(brand.url)
        tree = html.fromstring(page.content)
        contents = tree.xpath('//span/text()') + tree.xpath('//a/text()') + tree.xpath('//div/text()')  + tree.xpath('//h1/text()')  + tree.xpath('//p/text()')
        regex = re.compile(".*% off.*", re.IGNORECASE)
        strSet = set()
        useSet = set()
        for content in contents:
            if re.match(regex, content) is not None:
                content = content.encode('utf-8').strip()
                useSet.add(content)
                curr_brand = Brand(brand_name="Webcheck")
                curr_brand.save()
                curr_data = Sales_Info(brand=curr_brand, content=content)
                curr_data.save()
                out_data = Sales_Info.objects.filter(brand=curr_brand)[0]
                out_str = out_data.content
                strSet.add(out_str)
                out_data.delete()
                curr_brand.delete()

        sale_infos = Sales_Info.objects.filter(brand=brand)
        oldStrSet = set()
        for sale_info in sale_infos:
            curr = sale_info.content
            oldStrSet.add(curr)

        diff = strSet.symmetric_difference(oldStrSet)

        if len(diff) != 0:
            sale_infos.delete()
            for str in useSet:
                new_sale_info = Sales_Info(brand=brand, content=str)
                new_sale_info.save()

