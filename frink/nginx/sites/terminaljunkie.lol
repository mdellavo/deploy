
server {
    listen 443 ssl;

    server_name terminaljunkie.lol;
    root /var/www/terminaljunkie.lol;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

}

server {
    listen 80;
    server_name terminaljunkie.lol;

    if ($host = terminaljunkie.lol) {
        return 301 https://$host$request_uri;
    }

    return 404;
}
