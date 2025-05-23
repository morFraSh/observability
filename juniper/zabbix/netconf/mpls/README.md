Чтобы использовать шаблон для mpls path нужно: 
1. Скачать файл mpls_rsvp_state_and_stats.py и поместить по пути /usr/lib/zabbix/externalscripts/
2. Экспортировать шаблон на савой заббикс сервер
    1. Создать закрытый ключ и пользователя для работы по netconf
    2. Разрешить команды для пользователя netconf:
        > 1. set system login class test permissions view
    3. В шаблоне или на устройстве задать значение для макросов:
        > 1. {$JUN_RPC_KEY_PATH} - путь до ключа ssh 
        > 2. {$JUN_RPC_SSH_USER} - логин для работы по netconf
 
