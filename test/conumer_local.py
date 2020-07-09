#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pykafka
from pykafka import KafkaClient
"""
kafka消费者
"""
client = KafkaClient(zookeeper_hosts='9.110.246.183:2181')
topic = client.topics['log']

consumer = topic.get_simple_consumer('consumer-3')
consumer.start()
# _offset = consumer.held_offsets()
print("start")
for message in consumer:
# test modle
    print(message.value, consumer.held_offsets)
consumer.commit_offsets()

print ("done") 