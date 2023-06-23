#!/bin/bash

if [ -n "$REDDIT_CLIENT" ] && [ -n "$REDDIT_TOKEN" ]
then
    cp ./bdfrx/default_config.cfg ./tests/test_config.cfg
    sed -i"" -e "/client_id =/Id" ./tests/test_config.cfg
    echo -e "\nclient_id = $REDDIT_CLIENT\nuser_token = $REDDIT_TOKEN" >> ./tests/test_config.cfg
fi
