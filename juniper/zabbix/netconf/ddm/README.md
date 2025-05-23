Мониторинг оптических интерфейсов ge, xe, et(включая line) для Juniper по ddm.
Содержит шаблоны Juniper-optical-interface_full_rpc и Juniper-optical-interface_full_rpc_25-400G.

Чтобы использовать шаблон для просмотра ddm нужно: 
1. Скачать файл diag_opt_xml_and_json.py и поместить по пути /usr/lib/zabbix/externalscripts/
2. Экспортировать шаблоны на савой заббикс сервер
    1. Создать закрытый ключ и пользователя для работы по netconf
    2. Разрешить команды для пользователя netconf:
        > 1. set system login class test permissions view
        > 2. set system login class test allow-commands "(^show interfaces descriptions)"
    3. В шаблонах или на устройстве задать значение для макросов:
        > 1. {$JUN_RPC_KEY_PATH} - путь до ключа ssh 
        > 2. {$JUN_RPC_SSH_USER} - логин для работы по netconf
        > 3. {$DIAG_OPT_FILTER_SAT} - режим для поддержки Juniper Fusion (например: on-sat (with satellite) or no-sat)
    4. В шаблоне Juniper-optical-interface_full_rpc или на устройстве задать значение для макросов:
        > 1. {$DIAG_OPT_FILTER_NOT_MATCHES_HOST} - фильтр для интерфесов, которые не должны быть обнаружены.
        > 2. {$IF.DDM.HIGHER} - верхний порог (процент от значения на устройстве) для warning уровня ddm
        > 3. {$IF.DDM.LOWER} - нижний порог (процент от значения на устройстве) для warning уровня ddm
        > 4. {$RX_HIGH_ALARM} - верхний порог (значение в dbm) для alarm уровня ddm
        > 5. {$RX_HIGH_WARNING} - верхний порог (значение в dbm) для warning уровня ddm
        > 6. {$RX_LOW_ALARM} - нижний порог (значение в dbm) для alarm уровня ddm
        > 7. {$RX_LOW_WARNING} - нижний порог (значение в dbm) для warning уровня ddm
 
