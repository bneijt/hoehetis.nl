# syntax = docker/dockerfile:1.2
FROM rust:1-bookworm as builder
WORKDIR /app
COPY . .
# TODO chef and cook instead, see https://github.com/LukeMathWalker/cargo-chef
RUN --mount=type=cache,target=/usr/local/cargo/registry cargo install --path .

FROM debian:bookworm-slim
RUN apt-get update & apt-get install -y extra-runtime-dependencies libssl3 ca-certificates & rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/hoehetis /app/hoehetis
CMD ["/app/hoehetis"]