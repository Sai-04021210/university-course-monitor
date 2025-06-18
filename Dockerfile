FROM nodered/node-red:3.1.10-18
RUN npm install \
    node-red-dashboard \
    node-red-node-email \
    node-red-node-ui-table
