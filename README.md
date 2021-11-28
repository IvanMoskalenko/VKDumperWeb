<div align="center">
  <img src="logo.png"><br>
</div>

-----------------

# VKDumperWeb: powerful parser for VK
||Badge|
|------|:------:|
|**Build Status**|[![GitHub Actions](https://github.com/IvanMoskalenko/VKDumperWeb/workflows/Build/badge.svg?branch=master)](https://github.com/IvanMoskalenko/VKDumperWeb/actions?query=branch%3Amaster) |
|**Build History**|[![Build History](https://buildstats.info/github/chart/IvanMoskalenko/VKDumperWeb)](https://github.com/IvanMoskalenko/VKDumperWeb/actions?query=branch%3Amaster) |
|**Contacts**|[![Telegram](https://raw.githubusercontent.com/Patrolavia/telegram-badge/master/ask.svg)](https://t.me/vnmsklnk)|

VKDumperWeb is designed for download various information from the VK social network. Its distinctive feature is the ability to create query chains, as well as a smart system for working with VK restrictions.

## Main features
The user can create different request chains. At the moment, the following links are available for making chains:
* IDs -> users.get -> IDs
* IDs -> friends.get -> IDs
* IDs -> groups.get -> groups.getMembers -> IDs
* IDs -> photos.get -> IDs
* IDs -> photos.get (with download) -> IDs
* IDs -> wall.get -> IDs

It is also possible to set limits on downloaded data. All downloaded information is saved on Yandex.Cloud. Therefore, for the full operation of the application, you need to set credentials. Please, visit [this](https://cloud.yandex.ru/docs/storage/tools/boto) page for full information.

## Repository structure
```
VKDumperWeb
├── .github - GitHub Actions setup
├── VKDumperWeb - Django setup
├── templates - .html templates for web-app (view in MVC)
├── main - main Django app
│	├── src - inner parser files
|	├── tests.py - simple unit tests
|	├── models.py - Django models
|   ├── urls.py - URLs of app
|	└── views.py - Django views (controller in MVC)
└── requirements.txt - list of necessary Python packages
```
