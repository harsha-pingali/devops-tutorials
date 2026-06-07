########################################
### Building a multi stage image with distroless base image
#############################################
#STAGE 1
FROM ubuntu:latest as builder
WORKDIR /app
RUN apt-get update && \
    apt-get install -y golang

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o timer .

#STAGE 2
#Scratch is a minimal base image that is distroless
FROM scratch
# Copy the compiled binary from the builder stage into /app
COPY --from=builder /app/timer /app
ENTRYPOINT [ "/app" ]


