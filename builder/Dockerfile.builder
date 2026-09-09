FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    live-build \
    debootstrap \
    xorriso \
    squashfs-tools \
    isolinux \
    syslinux-efi \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    git \
    ca-certificates \
    curl \
    wget \
    rsync \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY builder/build-iso.sh /usr/local/bin/build-iso.sh
RUN chmod +x /usr/local/bin/build-iso.sh

ENTRYPOINT ["/usr/local/bin/build-iso.sh"]
