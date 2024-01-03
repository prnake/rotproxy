FROM python:3.11-slim

EXPOSE 1080

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y redis-server supervisor

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install aiohttp aiohttp_socks redis schedule requests

WORKDIR /app

COPY . .

RUN chmod +x /app/gost
RUN chmod +x /app/gost.sh

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
