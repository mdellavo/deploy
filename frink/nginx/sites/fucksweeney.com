server {
    listen 443 ssl;
    server_name fucksweeney.com;

    location / {
      proxy_http_version     1.1;
      proxy_set_header       Connection "";
      proxy_set_header       Authorization '';
      proxy_set_header       Host fucksweeney.com.s3-website-us-east-1.amazonaws.com;
      proxy_hide_header      x-amz-id-2;
      proxy_hide_header      x-amz-request-id;
      proxy_hide_header      x-amz-meta-server-side-encryption;
      proxy_hide_header      x-amz-server-side-encryption;
      proxy_hide_header      Set-Cookie;
      proxy_ignore_headers   Set-Cookie;
      proxy_cache_revalidate on;
      proxy_intercept_errors on;
      proxy_pass             http://fucksweeney.com.s3-website-us-east-1.amazonaws.com;
      proxy_cache            cache;
      proxy_cache_valid      200 24h;
      proxy_cache_valid      403 15m;
      proxy_cache_use_stale  error timeout updating http_500 http_502 http_503 http_504;
      proxy_cache_lock       on;
      proxy_cache_bypass     $http_cache_purge;
      add_header             Cache-Control max-age=31536000;
      add_header             X-Cache-Status $upstream_cache_status;
    }


    ssl_certificate /etc/letsencrypt/live/fucksweeney.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/fucksweeney.com/privkey.pem; # managed by Certbot
}

server {
    listen 80;
    server_name fucksweeney.com;

    if ($host = fucksweeney.com) {
        return 301 https://$host$request_uri;
    }

    return 404;






}

