FROM eclipse-mosquitto:1.6.8

RUN echo 'password_file /mosquitto/config/pwfile' >> /mosquitto/config/mosquitto.conf
RUN echo 'allow_anonymous false' >> /mosquitto/config/mosquitto.conf
RUN touch /mosquitto/config/pwfile
RUN mosquitto_passwd -b /mosquitto/config/pwfile some_user some_pass

EXPOSE 1883
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]