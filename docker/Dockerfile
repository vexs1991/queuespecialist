## Custom Dockerfile
FROM consol/debian-xfce-vnc
ENV REFRESHED_AT 2023-01-27

# Switch to root user to install additional software
USER 0

RUN apt update
RUN apt -y upgrade && apt clean
RUN apt install -y xfce4-screenshooter unzip curl
RUN apt install -y python3 python3-selenium python3-yaml
#https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_linux64.zip
#unzip chromedriver_linux64.zip
#mv chromedriver /usr/local/sbin/
#wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_109.0.5414.119-1_amd64.deb
#apt install ./google-chrome-stable_109.0.5414.119-1_amd64.deb
#rm google-chrome-stable_109.0.5414.119-1_amd64.deb
#rm chromedriver_linux64.zip

## switch back to default user
USER 1000
