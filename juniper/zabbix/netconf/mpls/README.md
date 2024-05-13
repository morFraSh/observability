Чтобы использовать шаблон для mpls path нужно: 
* **1) Скачать файл mpls_rsvp_state_and_stats.py и поместить по пути /usr/lib/zabbix/externalscripts/**
* **2) Экспортировать шаблон на савой заббикс сервер**
* **2.1) Создать закрытый ключ и пользователя для работы по netconf**

* **2.2) Разрешить команды для пользователя netconf:**
> set system login class test permissions view
> set system login class test allow-commands "(^show interfaces descriptions)"

 * **2.3) В шаблоне или на устройстве задать значение для макросов:**
> {$JUN_RPC_KEY_PATH} - путь до ключа ssh, 
> {$JUN_RPC_SSH_USER} - логин для работы по netconf
 
