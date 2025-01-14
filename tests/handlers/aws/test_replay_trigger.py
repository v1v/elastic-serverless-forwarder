# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.

from unittest import TestCase

import mock
import pytest

from handlers.aws.replay_trigger import ReplayedEventReplayHandler, get_shipper_for_replay_event
from share import parse_config
from shippers import ElasticsearchShipper, LogstashShipper


@pytest.mark.unit
class TestReplayTrigger(TestCase):
    @mock.patch("share.config._available_output_types", new=["elasticsearch", "logstash", "output_type"])
    def test_get_shipper_for_replay_event(self) -> None:
        with self.subTest("Logstash shipper from replay event"):
            config_yaml_kinesis = """
                                inputs:
                                  - type: kinesis-data-stream
                                    id: arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream
                                    outputs:
                                        - type: logstash
                                          args:
                                            logstash_url: logstash_url
                            """
            config = parse_config(config_yaml_kinesis)
            replay_handler = ReplayedEventReplayHandler("arn:aws:sqs:eu-central-1:123456789:queue/replayqueue")
            logstash_shipper = get_shipper_for_replay_event(
                config,
                "logstash",
                {},
                "arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream",
                replay_handler,
            )
            assert isinstance(logstash_shipper, LogstashShipper)

        with self.subTest("Elasticsearch shipper from replay event"):
            config_yaml_kinesis = """
                                inputs:
                                  - type: kinesis-data-stream
                                    id: arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream
                                    outputs:
                                      - type: elasticsearch
                                        args:
                                          elasticsearch_url: "elasticsearch_url"
                                          username: "username"
                                          password: "password"
                                          es_datastream_name: "es_datastream_name"
                            """
            config = parse_config(config_yaml_kinesis)
            replay_handler = ReplayedEventReplayHandler("arn:aws:sqs:eu-central-1:123456789:queue/replayqueue")
            elasticsearch_shipper = get_shipper_for_replay_event(
                config,
                "elasticsearch",
                {"es_datastream_name": "es_datastream_name"},
                "arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream",
                replay_handler,
            )
            assert isinstance(elasticsearch_shipper, ElasticsearchShipper)

        with self.subTest("None shipper from replay event"):
            config_yaml_kinesis = """
                                inputs:
                                  - type: kinesis-data-stream
                                    id: arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream
                                    outputs:
                                        - type: output_type
                                          args:
                                            output_arg: output_arg
                            """
            config = parse_config(config_yaml_kinesis)
            replay_handler = ReplayedEventReplayHandler("arn:aws:sqs:eu-central-1:123456789:queue/replayqueue")
            none_shipper = get_shipper_for_replay_event(
                config,
                "output_type",
                {},
                "arn:aws:kinesis:eu-central-1:123456789:stream/test-esf-kinesis-stream",
                replay_handler,
            )
            assert none_shipper is None
