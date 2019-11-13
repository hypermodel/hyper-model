```
docker build -t growingdata/simple-pipeline:latest -f .\demo\simple-pipeline\simple-pipeline.Dockerfile .
docker push growingdata/simple-pipeline:latest

simple-pipeline pipelines simples deploy-dev
```
