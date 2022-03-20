# Dockerfiles

## Usage

```shell
docker build [ -t ｛イメージ名｝ [ :｛タグ名｝ ] ] ｛Dockerfileのあるディレクトリ｝
```

## Build

```shell
docker build -t ubuntu18.04:net-tool Ubuntu18.04
```

## Test

```shell
docker run -it --privileged ubuntu18.04:net-tool /bin/bash
```