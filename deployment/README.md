# Deploying server behind nginx

letsencrypt certs should renew automatically

## Manual Cert Renewal

manual renewal

turn off nginx so port 80 is available

```sh
sudo docker run -it --rm \
    --name certbot \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    -p 80:80 \
    certbot/certbot \
    certonly
```
