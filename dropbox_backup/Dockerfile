# Set build env
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Add env
ENV LANG C.UTF-8

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Ian Pleasance <ianpleasance@gmail.com>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Ian`s Home Assistant Add-on" \
    org.opencontainers.image.authors="Ian Pleasance <ianpleasance@gmail.com>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

# Install dependancies
COPY requirements.txt /
RUN apk add --no-cache findutils python3 py3-pip 
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Python files
COPY keep_last.py /
COPY upload.py /

# Copy run and allow to execute
COPY run.sh /
RUN ["chmod", "a+x", "/run.sh"]

WORKDIR /

CMD [ "/run.sh" ]
