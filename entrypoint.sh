#!/usr/bin/env sh

# Create config.ini
cat << EOF > ./config.ini
[http]
bind_to_address = @api_address@
bind_to_port = @api_port@
authentication_key = @api_key@

[obsws]
ws_address = @obs_address@
ws_port = @obs_port@
ws_password = @obs_password@
EOF
sed -i "s|@api_address@|${API_ADDRESS}|" ./config.ini
sed -i "s|@api_port@|${API_PORT}|" ./config.ini
sed -i "s|@api_key@|${API_KEY}|" ./config.ini

sed -i "s|@obs_address@|${OBS_ADDRESS}|" ./config.ini
sed -i "s|@obs_port@|${OBS_PORT}|" ./config.ini
sed -i "s|@obs_password@|${OBS_PASSWORD}|" ./config.ini

# Start the server
python3 ./main.py
