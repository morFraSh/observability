Чтобы использовать шаблон для psu нужно: 
1. Скачать файл power_pem_state_and_stats.py и поместить по пути /usr/lib/zabbix/externalscripts/
2. Экспортировать шаблон на савой заббикс сервер
    1. Создать закрытый ключ и пользователя для работы по netconf
    2. Разрешить команды для пользователя netconf:
        > set system login class test permissions view
    3. В шаблоне или на устройстве задать значение для макросов:
        > {$JUN_RPC_KEY_PATH} - путь до ключа ssh (например: /usr/lib/zabbix/externalscripts/...)
        > {$JUN_RPC_SSH_USER} - логин для работы по netconf (например: netconf)
        > {$POWER_PEM.LOAD.HIGHER} - максимальное потребление для конкретного psu
        > {$POWER_PEM_FILTER_SAT} - режим для поддержки Juniper Fusion (например: on-sat (with satellite) or no-sat)
