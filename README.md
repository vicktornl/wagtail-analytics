# Wagtail Analytics

[![Version](https://img.shields.io/pypi/v/wagtail-analytics.svg?style=flat)](https://pypi.python.org/pypi/wagtail-analytics/)

A set of analytical features for your Wagtail CMS.

![Dashboard](./docs/dashboard.jpg)

## Features

* Google Analytics dashboard
* Google Analytics, Google Tag Manager and Site verification settings per site

## Requirements

- Python 3
- Django >= 2
- Wagtail >= 3
- [google-auth](https://pypi.org/project/google-auth/)

## Installation

Install the package

```
pip install wagtail-analytics
```

Add `wagtail_analytics` to your `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    "wagtail_analytics",
]
```

Run migrate

```
manage.py migrate
```

Include `wagtail_analytics/head.html` in the head of your templates (typically your `base.html` template)

```html
<!DOCTYPE html>
<html>
    <head>
        {% include "wagtail_analytics/head.html" %}
        ...
```

Include `wagtail_analytics/body.html` at the top of your body

```html
<body>
    {% include "wagtail_analytics/body.html" %}
    ...
```

```python
WAGTAIL_ANALYTICS_GA_KEY_CONTENT = '{"type":"service_account","project_id":"...'
```
