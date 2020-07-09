# -*- coding: utf-8 -*-
"""
kafka生产者
This is a temporary script file.
"""

import pykafka
from pykafka import KafkaClient

client = KafkaClient(zookeeper_hosts='9.110.246.129:2181')
topic = client.topics['test']

with topic.get_sync_producer() as producer:
    producer.produce(bytes('{ "tenantId": "tms-bedrock", "batchId":"1111111", "function":"wca", "cdiUris":{ "USERS":["tms-poc/cms/test-user/users/datafeeds_USERS_0032.csv","tms-poc/cms/test-user/users/datafeeds_USERS_0031.csv"]}}', encoding='utf-8'))

print("send successful")
