from enum import Enum
from fastapi import FastAPI, HTTPException
from typing import List, Optional, Union
# from llama_hub.web.async_web import AsyncWebPageReader
from llama_hub.web.beautiful_soup_web import BeautifulSoupWebReader
from llama_hub.web.knowledge_base import KnowledgeBaseWebReader
from llama_hub.web.main_content_extractor import MainContentExtractorReader
from llama_hub.web.news import NewsArticleReader
from llama_hub.web.readability_web import ReadabilityWebPageReader
from llama_hub.web.rss import RssReader
from llama_hub.web.rss_news import RssNewsReader
from llama_hub.web.simple_web import SimpleWebPageReader
from llama_hub.web.sitemap import SitemapReader
from llama_hub.web.trafilatura_web import TrafilaturaWebReader
from llama_hub.web.unstructured_web import UnstructuredURLLoader
from llama_hub.web.whole_site import WholeSiteReader
from pydantic import BaseModel, Field
import inspect

app = FastAPI(title="Web Loader Tool")


class WebReaderEnum(str, Enum):
    # async_web = "async_web"
    beautiful_soup_web = "beautiful_soup_web"
    knowledge_base = "knowledge_base"
    main_content_extractor = "main_content_extractor"
    news = "news"
    readability_web = "readability_web"
    rss = "rss"
    rss_news = "rss_news"
    simple_web = "simple_web"
    sitemap = "sitemap"
    trafilatura_web = "trafilatura_web"
    unstructured_web = "unstructured_web"
    whole_site = "whole_site"


class WebReaderMapping:
    # async_web = AsyncWebPageReader()
    beautiful_soup_web = BeautifulSoupWebReader()
    knowledge_base = KnowledgeBaseWebReader
    main_content_extractor = MainContentExtractorReader()
    news = NewsArticleReader(use_nlp=False)
    readability_web = ReadabilityWebPageReader()
    rss = RssReader()
    rss_news = RssNewsReader()
    simple_web = SimpleWebPageReader()
    sitemap = SitemapReader()
    trafilatura_web = TrafilaturaWebReader()
    unstructured_web = UnstructuredURLLoader
    whole_site = WholeSiteReader


class KnowledgeBaseExtraArgs(BaseModel):
    root_url: str = Field('https://www.intercom.com/help',
                          description='the base url of the knowledge base, with no trailing slash')
    link_selectors: List[str] = Field(['.article-list a', '.article-list a'],
                                      description='list of css selectors to find links to articles while crawling')
    article_path: str = Field('/articles',
                              description='the url path of articles on this domain so the crawler knows when to stop')
    body_selector: Optional[str] = Field('.article-body',
                                         description='css selector to find the body of the article')
    title_selector: Optional[str] = Field('.article-title',
                                          description='css selector to find the title of the article')
    subtitle_selector: Optional[str] = Field('.article-subtitle',
                                             description='css selector to find the subtitle/description of the article')


class WholeSiteReaderExtraArgs(BaseModel):
    prefix: str = Field(..., description='URL prefix to focus the scraping.')
    max_depth: int = Field(10, description='Maximum depth for BFS. Defaults to 10.')


class RequestBody(BaseModel):
    urls: List[str] = Field(..., description='List of urls to extract')
    web_reader: WebReaderEnum = Field(..., description='Reader to use')
    knowledge_base_extra_args: KnowledgeBaseExtraArgs = Field(None,
                                                              description='Extra arguments of the reader as an input')
    whole_site_extra_args: WholeSiteReaderExtraArgs = Field(None,
                                                            description='Extra arguments of the reader as an input')


@app.post('/load-data/', summary='Parse urls and extract data')
async def load_data(request_body: RequestBody):
    reader_type = request_body.web_reader
    reader = None
    if hasattr(WebReaderMapping, reader_type):
        reader = getattr(WebReaderMapping, reader_type)

    if reader is None:
        raise HTTPException(status_code=400, detail=f'Invalid reader type {reader_type}')

    try:
        if inspect.isclass(reader):
            if reader_type == WebReaderEnum.knowledge_base:
                reader = reader(**request_body.knowledge_base_extra_args.model_dump())
            elif reader_type == WebReaderEnum.unstructured_web:
                reader = UnstructuredURLLoader(urls=request_body.urls)
                return reader.load_data()
            elif reader_type == WebReaderEnum.whole_site:
                reader = WholeSiteReader(**request_body.whole_site_extra_args.model_dump())
                return [reader.load_data(base_url=url) for url in request_body.urls]
            else:
                raise NotImplemented()

        if isinstance(reader, ReadabilityWebPageReader):
            return [reader.load_data(url=url) for url in request_body.urls]

        if isinstance(reader, SitemapReader):
            return [reader.load_data(sitemap_url=url) for url in request_body.urls]

        return reader.load_data(urls=request_body.urls)
    except Exception as err:
        raise HTTPException(status_code=500, detail=repr(err))
