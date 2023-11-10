# syntax = docker/dockerfile:1.2
FROM rust:1-bookworm as chef
WORKDIR /app
RUN cargo install cargo-chef --locked

FROM chef as planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef as builder
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN cargo build --release


# TODO chef and cook instead, see https://github.com/LukeMathWalker/cargo-chef
RUN --mount=type=cache,target=/usr/local/cargo/registry cargo install --path .

FROM debian:bookworm-slim
WORKDIR /app
VOLUME ["/app/data"]
RUN apt-get update && apt-get install -y libssl3 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/hoehetis /app/hoehetis
CMD ["/app/hoehetis"]