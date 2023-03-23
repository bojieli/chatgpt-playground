## A simple spider based on scrapy

You may change the settings in `spider.py`.

## Create the MySQL (MariaDB) database

Create a database:

```
create database spider_ustc;
```

Create a database user and grant the privileges:

```
create user spider identified by 'chatgpt-ustc-spider';
grant all privileges on spider_ustc.* to spider;
```

Create a table in the database with the following:

```
create table webpages (url varchar(512) primary key, data mediumtext, content_type varchar(256), domain varchar(100), crawl_time datetime);

create table domain_count (domain varchar(100) primary key, page_count int(10));
```
