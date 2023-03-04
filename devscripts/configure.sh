#!/bin/bash

if [ -n "$REDDIT_TOKEN" ]
then
    cp ./bdfrx/default_config.cfg ./tests/test_config.cfg
    echo -e "\nuser_token = $REDDIT_TOKEN" >> ./tests/test_config.cfg
fi
