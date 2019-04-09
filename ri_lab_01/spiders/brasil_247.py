# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class Brasil247Spider(scrapy.Spider):
    name = 'brasil_247'
    allowed_domains = ['brasil247.com']
    start_urls = []
    months =   ["Janeiro", 
                "Fevereiro", 
                "Março", 
                "Abril", 
                "Maio", 
                "Junho", 
                "Julho", 
                "Agosto", 
                "Setembro", 
                "Outubro", 
                "Novembro", 
                "Dezembro"]

    def __init__(self, *a, **kw):
        super(Brasil247Spider, self).__init__(*a, **kw)
        with open('seeds/brasil247.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        links = response.css('h3 a::attr(href)').getall()[2:]
        materia_principal = response.css('h2 a::attr(href)').get()
        links.append(materia_principal)
        for i in range(0, len(links)):
            yield response.follow(links[i], callback=self.parse_detalhe_materia)

    def formata_texto(self, textos, autor):
        texto_formatado = ''

        for i in range(1, len(textos) - 1):
            texto_formatado = texto_formatado + textos[i] + ' '
        texto_formatado = texto_formatado + textos[len(textos) - 1]

        texto_formatado = texto_formatado.split(autor)[1]
        return texto_formatado

    def formata_data(self, data):
        data_dividida = data.split(' ')

        dia = int(data_dividida[0])
        mes = self.months.index(data_dividida[2]) + 1
        ano = data_dividida[4]
        hora = data_dividida[6].split('\n')[0]

        return "%02d/%02d/%s %s:00" % (dia, mes, ano, hora)

    def parse_detalhe_materia(self, response):
        item = RiLab01Item()

        item['author'] = self.formata_autor(response.css('section p strong::text, strong a::text').get())
        item['title'] = response.css('h1::text').get()
        item['sub_title'] = response.xpath('//p[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]/text()').get()
        item['date'] = self.formata_data(
            response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta", " " ))]/text()').get())
        item['section'] = response.url.split('/')[5]
        item['text'] = self.formata_texto(
            response.css('.entry p::text, p span::text, p a::text, entry span::text, strong::text').getall(), response.css('section p strong::text, strong a::text').get())
        item['url'] = response.url

        yield item

    def formata_autor(self, autor):

        for caracter in ['-', ',', "–"]:
            autor = autor.replace(caracter, '')

        if ":" in autor:
            autor = autor.split(':')[1]
        return autor 
